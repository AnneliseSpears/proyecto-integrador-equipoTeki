"""
LeadSales · Monitor de adopción y riesgo de churn (Equipo Teki)

Pregunta directiva:
    ¿Cómo identificar si la baja adopción de funcionalidades y canales
    anticipa la cancelación?

Datos v3 (corte 31-oct-2026):
    - panel_mensual.csv   una fila por cuenta y mes (uso, días activos, plan...)
    - perfil_cuentas.csv  una fila por cuenta (fecha de baja = desenlace)
    - cancelaciones.csv   motivo que dio cada cuenta al cancelar
"""

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="LeadSales | Adopción y riesgo de churn", layout="wide")

# --- Rutas que no dependen de desde dónde se ejecute el comando ---
CARPETA_DATOS = Path(__file__).parent.parent / "datos"

CORTE_DATOS = pd.Timestamp("2026-10-31")  # último día con información
HORIZONTE_DIAS = 60  # ventana para decir si una cuenta canceló "pronto"
PRIMER_CORTE = pd.Timestamp("2026-05-01")  # se necesitan 2 meses previos para medir la caída

MESES_ES = {1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
            7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"}

NOMBRES_MOTIVOS = {
    "H2_technical_issues": "Problemas técnicos",
    "H4_lack_of_results": "No ve resultados",
    "H5_high_pricing": "Precio alto",
    "H6_plan_fit": "El plan no se ajusta",
    "H8_business_pause": "Pausa del negocio",
    "OTHER": "Otro motivo",
}

# La columna industria trae el mismo valor escrito de varias formas
INDUSTRIAS = {
    "Inmobiliaria": "Inmobiliaria y bienes raíces",
    "realestateeinmobiliaria": "Inmobiliaria y bienes raíces",
    "Real estate e inmobiliaria": "Inmobiliaria y bienes raíces",
    "Real Estate e Inmobiliaria": "Inmobiliaria y bienes raíces",
    "Real state": "Inmobiliaria y bienes raíces",
    "saludymedicina": "Servicios de salud y Bienestar",
    "Salud y medicina": "Servicios de salud y Bienestar",
    "Salud y Medicina": "Servicios de salud y Bienestar",
    "Salud y bienestar": "Servicios de salud y Bienestar",
    "Salones de belleza": "Servicios de salud y Bienestar",
    "ecommerce": "Ecommerce",
    "E-commerce": "Ecommerce",
    "serviciosprofesionales": "Servicios profesionales, técnicos y de consultoría",
    "Servicios profesionales": "Servicios profesionales, técnicos y de consultoría",
    "Servicios Profesionales": "Servicios profesionales, técnicos y de consultoría",
    "automotriz": "Automotriz",
    "educacin": "Servicios educativos",
    "Educación": "Servicios educativos",
    "viajesyturismo": "Hotelería, Turismo y Restaurantes",
    "Viajes y turismo": "Hotelería, Turismo y Restaurantes",
    "Tourism": "Hotelería, Turismo y Restaurantes",
    "Turismo": "Hotelería, Turismo y Restaurantes",
    "Restauración y alimentos": "Hotelería, Turismo y Restaurantes",
    "finanzasybanca": "Servicios financieros y Seguros",
    "Finanzas y banca": "Servicios financieros y Seguros",
    "Finance": "Servicios financieros y Seguros",
    "agenciasyconsultoria": "Agencias y Consultoría",
    "Agencias y consultoria": "Agencias y Consultoría",
    "Tecnología": "Informática y Software",
    "Entretenimiento": "Arte, Cultura, Deportes y Entretenimiento",
    "Otro": "Otra / no declarada",
    "No declarada": "Otra / no declarada",
}

COLOR_CON = "#C0392B"  # con caída de actividad
COLOR_SIN = "#7F8C8D"  # sin caída


def etiqueta_mes(fecha):
    return f"{MESES_ES[fecha.month]} {fecha.year}"


# --- Carga y preparación de datos (se guarda en caché) ---
@st.cache_data
def cargar(carpeta):
    panel = pd.read_csv(carpeta / "panel_mensual.csv", parse_dates=["mes"])
    perfil = pd.read_csv(carpeta / "perfil_cuentas.csv", parse_dates=["fecha_inicio", "fecha_baja"])
    cancelaciones = pd.read_csv(carpeta / "cancelaciones.csv", parse_dates=["fecha"])

    panel = panel.sort_values(["account_id", "mes"]).reset_index(drop=True)
    panel["industria"] = panel["industria"].replace(INDUSTRIAS).fillna("Otra / no declarada")
    panel = panel.merge(perfil[["account_id", "fecha_inicio", "fecha_baja"]], on="account_id", how="left")

    # Caída de chats: chats del mes contra el promedio de los dos meses anteriores.
    # Solo se puede medir si los dos meses previos existen, son consecutivos y la cuenta estaba activa.
    por_cuenta = panel.groupby("account_id")
    previo_1, previo_2 = por_cuenta["mes"].shift(1), por_cuenta["mes"].shift(2)
    consecutivos = (previo_1 == panel["mes"] - pd.DateOffset(months=1)) & (
        previo_2 == panel["mes"] - pd.DateOffset(months=2)
    )
    previos_activos = (por_cuenta["estado_en_mes"].shift(1) == "activa") & (
        por_cuenta["estado_en_mes"].shift(2) == "activa"
    )
    # Ventana completa: 3 meses seguidos activa y pagando desde el inicio (misma población que la Evidencia 4)
    panel["ventana_completa"] = (
        consecutivos & previos_activos & (panel["fecha_inicio"] <= panel["mes"] - pd.DateOffset(months=2))
    )
    panel["chats_base"] = (por_cuenta["n_chats"].shift(1) + por_cuenta["n_chats"].shift(2)) / 2
    medible = panel["ventana_completa"] & (panel["chats_base"] > 0)
    cociente = panel["n_chats"] / panel["chats_base"]
    panel["variacion_chats"] = np.where(medible, (cociente - 1) * 100, np.nan)
    panel["caida_50"] = np.where(medible, (cociente <= 0.5).astype(float), np.nan)

    # Frecuencia de uso: proporción de días del mes con actividad
    panel["prop_dias_activos"] = panel["dias_activos"] / panel["mes"].dt.days_in_month
    panel["nivel_adopcion"] = pd.cut(
        panel["prop_dias_activos"],
        bins=[-0.01, 0.25, 0.75, 1.01],
        labels=["Baja (<25% de días)", "Media (25–75%)", "Alta (>75%)"],
    ).astype(str)

    # Base del tablero: cuentas activas al cierre de cada mes (el "corte")
    base = panel[
        (panel["estado_en_mes"] == "activa") & panel["ventana_completa"] & (panel["mes"] >= PRIMER_CORTE)
    ].copy()
    base["corte"] = base["mes"] + pd.offsets.MonthEnd(0)
    base = base[base["fecha_baja"].isna() | (base["fecha_baja"] > base["corte"])]

    # Desenlace: ¿canceló en los 60 días siguientes al corte?
    # Solo se conoce si esos 60 días ya pasaron (sep y oct quedan sin desenlace).
    fin_ventana = base["corte"] + pd.Timedelta(days=HORIZONTE_DIAS)
    cancelo = (base["fecha_baja"] > base["corte"]) & (base["fecha_baja"] <= fin_ventana)
    base["churn_60d"] = np.where(fin_ventana <= CORTE_DATOS, cancelo.astype(float), np.nan)

    # Actividad en los meses previos a la baja (para ver si el uso cae antes de cancelar)
    con_baja = panel[panel["fecha_baja"].notna() & panel["estado_en_mes"].isin(["activa", "baja_este_mes"])].copy()
    mes_baja = con_baja["fecha_baja"].dt.to_period("M")
    con_baja["meses_antes"] = (
        (mes_baja.dt.year - con_baja["mes"].dt.year) * 12 + (mes_baja.dt.month - con_baja["mes"].dt.month)
    )
    antes_baja = con_baja[con_baja["meses_antes"].between(0, 4)]

    # Motivo de cancelación: la última respuesta de cada cuenta
    motivos = (
        cancelaciones.sort_values("fecha")
        .drop_duplicates("account_id", keep="last")[["account_id", "motivo_normalizado", "detalle_texto"]]
    )
    motivos["motivo"] = motivos["motivo_normalizado"].map(NOMBRES_MOTIVOS).fillna("Otro motivo")

    return base, antes_baja, motivos


base, antes_baja, motivos = cargar(CARPETA_DATOS)

# --- Barra lateral: marca y filtros (opciones generadas desde los datos) ---
with st.sidebar:
    st.markdown("## LeadSales")
    st.caption("Adoption & Churn Monitor")
    st.divider()
    st.header("Filtros")

    cortes = sorted(base["corte"].unique())
    inicio, fin = st.select_slider(
        "Periodo (mes de corte)",
        options=cortes,
        value=(cortes[0], cortes[-1]),
        format_func=etiqueta_mes,
    )

    planes = st.multiselect(
        "Plan",
        options=sorted(base["plan"].dropna().unique()),
        default=sorted(base["plan"].dropna().unique()),
    )
    segmentos = st.multiselect(
        "Segmento",
        options=sorted(base["segmento"].dropna().unique()),
        default=sorted(base["segmento"].dropna().unique()),
    )
    industrias = st.multiselect(
        "Industria",
        options=sorted(base["industria"].unique()),
        default=sorted(base["industria"].unique()),
    )

# --- Un solo bloque de filtrado ---
filtrados = base[
    base["corte"].between(inicio, fin)
    & base["plan"].isin(planes)
    & base["segmento"].isin(segmentos)
    & base["industria"].isin(industrias)
]

# --- Encabezado ---
st.title("Monitor de adopción y riesgo de churn")
st.markdown(
    "**¿La baja adopción anticipa la cancelación?** Comparamos cuántas cuentas cancelan en los "
    "60 días siguientes al cierre de cada mes, según cómo venían usando LeadSales."
)
st.caption(f"Periodo: {etiqueta_mes(inicio)} a {etiqueta_mes(fin)} · Datos al 31-oct-2026")

if filtrados.empty:
    st.warning("No hay cuentas con esos filtros. Amplía la selección.")
    st.stop()

con_desenlace = filtrados[filtrados["churn_60d"].notna()]
medibles = filtrados[filtrados["caida_50"].notna()]
ultimo_corte = filtrados["corte"].max()

# --- Indicadores ---
activas_ultimo = filtrados.loc[filtrados["corte"] == ultimo_corte, "account_id"].nunique()
pct_caida = medibles["caida_50"].mean() * 100 if not medibles.empty else np.nan

c1, c2, c3, c4 = st.columns(4)
c1.metric("Cuentas activas", f"{activas_ultimo:,}", help=f"Al cierre de {etiqueta_mes(ultimo_corte)}")
c2.metric(
    "Con caída ≥50% de chats",
    f"{pct_caida:.1f}%" if pd.notna(pct_caida) else "Sin dato",
    help="Chats del mes contra el promedio de los dos meses anteriores",
)

if con_desenlace.empty:
    c3.metric("Churn a 60 días", "Sin desenlace")
    c4.metric("Riesgo con caída", "Sin desenlace")
    st.info(
        "Los cortes de septiembre y octubre todavía no tienen desenlace a 60 días. "
        "Incluye algún mes entre mayo y agosto para ver el churn."
    )
else:
    churn_total = con_desenlace["churn_60d"].mean() * 100
    churn_con = con_desenlace.loc[con_desenlace["caida_50"] == 1, "churn_60d"].mean() * 100
    churn_sin = con_desenlace.loc[con_desenlace["caida_50"] == 0, "churn_60d"].mean() * 100
    veces = churn_con / churn_sin if churn_sin > 0 else np.nan

    c3.metric("Churn a 60 días", f"{churn_total:.1f}%", help="Cuentas que cancelan en los 60 días siguientes al corte")
    c4.metric(
        "Riesgo con caída",
        f"{veces:.1f}× más" if pd.notna(veces) else "Sin dato",
        help="Cuántas veces más cancelan las cuentas con caída que las cuentas sin caída",
    )
    if pd.notna(veces):
        c4.caption(f"{churn_con:.0f}% de churn con caída vs {churn_sin:.0f}% sin caída")

st.divider()

# --- Bloque intermedio: dos gráficas lado a lado ---
izq, der = st.columns(2)

if con_desenlace.empty:
    izq.info("Sin desenlace en el periodo elegido.")
    der.info("Sin desenlace en el periodo elegido.")
else:
    por_corte = (
        con_desenlace.dropna(subset=["caida_50"])
        .groupby(["corte", "caida_50"], as_index=False)["churn_60d"]
        .mean()
    )
    por_corte["churn_%"] = por_corte["churn_60d"] * 100
    por_corte["Mes de corte"] = por_corte["corte"].map(etiqueta_mes)
    por_corte["Actividad"] = por_corte["caida_50"].map({1.0: "Con caída ≥50%", 0.0: "Sin caída"})

    fig_corte = px.bar(
        por_corte,
        x="Mes de corte",
        y="churn_%",
        color="Actividad",
        barmode="group",
        text_auto=".0f",
        title="Churn a 60 días: cuentas con caída de chats vs sin caída",
        labels={"churn_%": "Churn a 60 días (%)"},
        color_discrete_map={"Con caída ≥50%": COLOR_CON, "Sin caída": COLOR_SIN},
    )
    fig_corte.add_hline(y=churn_total, line_dash="dot", annotation_text="Promedio")
    izq.plotly_chart(fig_corte, width="stretch")

    por_nivel = con_desenlace.groupby("nivel_adopcion", as_index=False).agg(
        churn=("churn_60d", "mean"), cuentas=("account_id", "size")
    )
    por_nivel["churn_%"] = por_nivel["churn"] * 100
    orden_niveles = ["Baja (<25% de días)", "Media (25–75%)", "Alta (>75%)"]

    der.plotly_chart(
        px.bar(
            por_nivel,
            x="churn_%",
            y="nivel_adopcion",
            orientation="h",
            text_auto=".1f",
            title="Churn a 60 días según los días activos del mes",
            labels={"churn_%": "Churn a 60 días (%)", "nivel_adopcion": "Días activos en el mes"},
            category_orders={"nivel_adopcion": orden_niveles},
            hover_data={"cuentas": True},
            color_discrete_sequence=[COLOR_SIN],
        ),
        width="stretch",
    )

# --- Bloque inferior: detalle en pestañas ---
tab1, tab2, tab3, tab4 = st.tabs(
    ["Cuentas con mayor caída", "Uso antes de cancelar", "¿Por qué se van?", "Cómo leer el tablero"]
)

with tab1:
    st.subheader(f"Cuentas con caída ≥50% de chats al cierre de {etiqueta_mes(ultimo_corte)}")

    en_riesgo = filtrados[(filtrados["corte"] == ultimo_corte) & (filtrados["caida_50"] == 1)].copy()
    en_riesgo["desenlace"] = en_riesgo["churn_60d"].map({1.0: "Canceló", 0.0: "Sigue activa"}).fillna("Aún sin desenlace")
    en_riesgo["prop_dias_activos"] = (en_riesgo["prop_dias_activos"] * 100).round(0)
    en_riesgo["chats_base"] = en_riesgo["chats_base"].round(0)
    en_riesgo["variacion_chats"] = en_riesgo["variacion_chats"].round(0)

    tabla = (
        en_riesgo.sort_values("variacion_chats")[
            ["account_id", "plan", "segmento", "industria", "n_chats", "chats_base",
             "variacion_chats", "prop_dias_activos", "desenlace"]
        ]
        .rename(
            columns={
                "account_id": "Account ID",
                "plan": "Plan",
                "segmento": "Segmento",
                "industria": "Industria",
                "n_chats": "Chats del mes",
                "chats_base": "Chats promedio (2 meses previos)",
                "variacion_chats": "Variación (%)",
                "prop_dias_activos": "Días activos (%)",
                "desenlace": "Desenlace a 60 días",
            }
        )
    )

    st.caption(
        f"{len(tabla):,} cuentas cumplen la señal. Son las primeras que Customer Success debería revisar."
    )
    st.dataframe(tabla, width="stretch", hide_index=True)
    st.download_button(
        "Descargar lista (CSV)",
        data=tabla.to_csv(index=False).encode("utf-8"),
        file_name=f"cuentas_con_caida_{ultimo_corte:%Y-%m}.csv",
        mime="text/csv",
    )

with tab2:
    st.subheader("¿El uso cae antes de cancelar?")

    bajas = antes_baja[
        antes_baja["plan"].isin(planes)
        & antes_baja["segmento"].isin(segmentos)
        & antes_baja["industria"].isin(industrias)
        & (antes_baja["fecha_baja"] > inicio)
        & (antes_baja["fecha_baja"] <= fin + pd.Timedelta(days=HORIZONTE_DIAS))
    ]

    if bajas.empty:
        st.info("No hay cuentas canceladas con esos filtros.")
    else:
        trayectoria = bajas.groupby("meses_antes", as_index=False).agg(
            dias_activos=("prop_dias_activos", "median"), cuentas=("account_id", "nunique")
        )
        trayectoria["dias_activos"] = trayectoria["dias_activos"] * 100
        trayectoria["Mes"] = trayectoria["meses_antes"].map(
            lambda m: "Mes de la baja" if m == 0 else f"{m} meses antes" if m > 1 else "1 mes antes"
        )
        trayectoria = trayectoria.sort_values("meses_antes", ascending=False)

        referencia = filtrados.loc[filtrados["churn_60d"] == 0, "prop_dias_activos"].median() * 100

        fig_tray = px.line(
            trayectoria,
            x="Mes",
            y="dias_activos",
            markers=True,
            title="Días activos (mediana) de las cuentas que cancelaron, en los meses previos a su baja",
            labels={"dias_activos": "Días activos del mes (%)", "Mes": ""},
            hover_data={"cuentas": True},
            color_discrete_sequence=[COLOR_CON],
        )
        if pd.notna(referencia):
            fig_tray.add_hline(y=referencia, line_dash="dot", annotation_text="Cuentas que se quedan")
        fig_tray.update_yaxes(range=[0, 105])
        st.plotly_chart(fig_tray, width="stretch")
        st.caption(
            f"{bajas['account_id'].nunique():,} cuentas canceladas. La línea punteada es la mediana de "
            "las cuentas que no cancelaron en el mismo periodo."
        )

with tab3:
    st.subheader("Motivo de cancelación de las cuentas que se fueron")

    canceladas = (
        con_desenlace[con_desenlace["churn_60d"] == 1]
        .sort_values("corte")
        .drop_duplicates("account_id", keep="last")
        .merge(motivos, on="account_id", how="inner")
    )

    if canceladas.empty:
        st.info("No hay respuestas de cancelación con esos filtros.")
    else:
        canceladas["Actividad al corte"] = canceladas["caida_50"].map(
            {1.0: "Con caída ≥50%", 0.0: "Sin caída"}
        ).fillna("No medible")
        por_motivo = canceladas.groupby(["motivo", "Actividad al corte"], as_index=False).size()

        st.plotly_chart(
            px.bar(
                por_motivo,
                x="size",
                y="motivo",
                color="Actividad al corte",
                orientation="h",
                title="¿Qué dijeron al cancelar?",
                labels={"size": "Cuentas", "motivo": ""},
                color_discrete_map={"Con caída ≥50%": COLOR_CON, "Sin caída": COLOR_SIN, "No medible": "#D5D8DC"},
            ),
            width="stretch",
        )
        st.caption(
            f"{len(canceladas):,} cuentas canceladas respondieron la encuesta de salida. "
            "La caída de uso dice **cuándo** actuar; el motivo dice **qué** ofrecer."
        )

        tabla_cruzada = canceladas.pivot_table(
            index="motivo", columns="plan", values="account_id", aggfunc="count", fill_value=0
        )
        st.dataframe(tabla_cruzada, width="stretch")

with tab4:
    st.markdown(
        """
**Qué responde este tablero.** Si la baja adopción anticipa la cancelación. Para cada cuenta activa al
cierre de un mes revisamos cómo venía usando LeadSales y si canceló en los **60 días siguientes**.

**Las dos señales de adopción**
- **Caída ≥50% de chats:** los chats del mes son la mitad o menos del promedio de los dos meses
  anteriores. Si ese promedio es 0 o falta un mes, la caída no se puede medir (no se toma como 0).
- **Días activos:** proporción de días del mes en los que la cuenta usó la plataforma.

**Qué encontramos (Evidencia 4).** Las cuentas con caída cancelan cerca de 3 veces más que las demás,
y la frecuencia de uso pesa más que el volumen de chats. La conexión de canales (por ejemplo, WhatsApp
Web) no anticipó la baja más allá de lo que ya dice el uso, y sus datos tienen problemas de calidad,
por eso no se grafica aquí.

**Limitaciones**
- Es una **asociación**, no una causa: una caída no significa que la cuenta se vaya a ir.
- Septiembre y octubre todavía no tienen desenlace a 60 días.
- Solo se incluyen cuentas con al menos 3 meses seguidos de historial; las cuentas nuevas (onboarding)
  necesitan otro seguimiento.
"""
    )
