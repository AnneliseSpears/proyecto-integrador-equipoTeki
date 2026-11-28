"""
LeadSales · Monitor de adopción y riesgo de churn (Equipo Teki)

Pregunta directiva:
    ¿Cómo identificar si la baja adopción de funcionalidades y canales
    anticipa la cancelación?

Datos v3 (corte 31-oct-2026):
    - panel_mensual.csv   una fila por cuenta y mes (uso, días activos, plan...)
    - perfil_cuentas.csv  una fila por cuenta (fecha de baja = desenlace)
    - cancelaciones.csv   motivo que dio cada cuenta al cancelar
    - scores_modelo_hoy.csv  score de riesgo (Extra Trees) y perfil (K-Means) de cada cuenta
                             al 31-oct-2026; lo genera el notebook de la Evidencia 5

Colores: misma paleta del prototipo de Figma (Evidencia 5). El tema general está en
.streamlit/config.toml y los colores de las gráficas, abajo (PALETA).
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

# --- Paleta del tablero (la misma del prototipo de Figma y del notebook de la Evidencia 5) ---
# Sale del azul de LeadSales #4145E3 con la teoría del color de la clase:
#   60 % fondo neutro · 30 % marca · 10 % acento (complementario, solo para acciones)
#   rojo, naranja y verde solo con su significado (riesgo, advertencia, éxito)
MARCA = "#4145E3"        # 30 % · serie de referencia ("sin la señal", "conectado")
RIESGO = "#DC2626"       # semántico · la señal de riesgo
ADVERTENCIA = "#C2410C"  # semántico · atención (pasa WCAG con texto blanco: 5.2:1)
NEUTRO = "#C5C9D4"       # casos que no se pueden medir

COLOR_CON = RIESGO  # con la señal de baja adopción
COLOR_SIN = MARCA   # sin la señal

# Perfiles de adopción del K-Means de la Evidencia 4: un color por perfil en todo el tablero
COLOR_PERFIL = {
    "Descenso de actividad": RIESGO,
    "Uso muy bajo o nulo": ADVERTENCIA,
    "Uso estable": MARCA,
}
ACCION_PERFIL = {
    "Descenso de actividad": "Primera prioridad: llamada de diagnóstico, revisar si WhatsApp Web está desconectado y ofrecer capacitación.",
    "Uso muy bajo o nulo": "Reactivación o ajuste de plan antes de su renovación.",
    "Uso estable": "Seguimiento normal; atender solo si entra al decil 1 o desconecta WhatsApp Web.",
}
UMBRAL_MODELO = 0.095  # umbral del modelo elegido con F2 en la Evidencia 4


def etiqueta_mes(fecha):
    return f"{MESES_ES[fecha.month]} {fecha.year}"


# --- Carga y preparación de datos (se guarda en caché) ---
# Señales de la Evidencia 4 que se comparan en el tablero: (tipo, nombre, columna)
SENALES = [
    ("Uso", "Caída ≥50% de chats", "caida_50"),
    ("Uso", "Uso bajo 2 meses seguidos (<50% de días)", "uso_bajo_2m"),
    ("Canal", "WhatsApp Web desconectado al cierre", "wa_desconectado"),
    ("Contexto", "En mora al cierre", "mora"),
    ("Contexto", "Abrió tickets de soporte (3 meses)", "tickets_3m"),
]


def estado_whatsapp(eventos, cortes):
    """Estado de WhatsApp Web al cierre de cada mes, con las reglas de la Evidencia 4:
    - solo cuentan los eventos hasta el día del corte;
    - una desconexión de menos de 24 h al corte queda como desconocida (puede ser un parpadeo);
    - si en el mismo instante hay conecta y desconecta, el estado es desconocido;
    - sin eventos en el periodo = la cuenta no usa WhatsApp Web (por ejemplo, usa la API).
    Solo se usa WhatsApp Web: Instagram, Facebook y la API tienen desconexiones faltantes y borrados masivos."""
    wa = eventos[eventos["canal"] == "whatsapp_web"].copy()
    wa["fecha_hora"] = pd.to_datetime(wa["fecha_hora"], utc=True).dt.tz_localize(None).astype("datetime64[ns]")
    wa["valor"] = wa["evento"].map({"conecta": 1, "conectado_al_inicio": 1, "desconecta": 0})
    wa = wa.groupby(["account_id", "fecha_hora"], as_index=False)["valor"].agg(["min", "max"])
    wa["valor"] = np.where(wa["min"] == wa["max"], wa["min"], -1)
    wa = wa.sort_values("fecha_hora")[["account_id", "fecha_hora", "valor"]]

    consulta = cortes.drop_duplicates().copy()
    consulta["limite"] = (consulta["corte"] + pd.Timedelta(days=1)).astype("datetime64[ns]")
    consulta = consulta.sort_values("limite")
    ultimo = pd.merge_asof(consulta, wa, left_on="limite", right_on="fecha_hora", by="account_id")
    reciente = (ultimo["limite"] - ultimo["fecha_hora"]) < pd.Timedelta(hours=24)
    ultimo["estado_wa"] = np.select(
        [ultimo["valor"].isna(), ultimo["valor"] == -1, ultimo["valor"] == 1, reciente],
        ["Sin WhatsApp Web", "Desconocido", "Conectado", "Desconocido"],
        default="Desconectado",
    )
    return ultimo[["account_id", "corte", "estado_wa"]]


def comparar_senales(df):
    """Churn a 60 días de los casos con y sin cada señal (solo cortes con desenlace)."""
    con_desenlace = df[df["churn_60d"].notna()]
    filas = []
    for tipo, nombre, columna in SENALES:
        evaluables = con_desenlace.dropna(subset=[columna])
        con = evaluables.loc[evaluables[columna] == 1, "churn_60d"]
        sin = evaluables.loc[evaluables[columna] == 0, "churn_60d"]
        if con.empty or sin.empty:
            continue
        filas.append({
            "Tipo": tipo,
            "Señal": nombre,
            "Casos con la señal (%)": round(len(con) / len(evaluables) * 100, 1),
            "Churn con la señal (%)": round(con.mean() * 100, 1),
            "Churn sin la señal (%)": round(sin.mean() * 100, 1),
            "Veces más": round(con.mean() / sin.mean(), 1) if sin.mean() > 0 else np.nan,
        })
    return pd.DataFrame(filas)


# Nombres cortos para las gráficas (la tabla conserva los nombres completos)
NOMBRE_CORTO = {
    "Caída ≥50% de chats": "Caída ≥50% de chats",
    "Uso bajo 2 meses seguidos (<50% de días)": "Uso bajo 2 meses",
    "WhatsApp Web desconectado al cierre": "WhatsApp Web desconectado",
    "En mora al cierre": "En mora",
    "Abrió tickets de soporte (3 meses)": "Tickets de soporte",
}
NIVEL_CORTO = {
    "Baja (<25% de días)": "Baja<br>(<25% de días)",
    "Media (25–75%)": "Media<br>(25–75%)",
    "Alta (>75%)": "Alta<br>(>75%)",
}


def figura_senales(tabla):
    datos = tabla.melt(
        id_vars=["Tipo", "Señal"],
        value_vars=["Churn con la señal (%)", "Churn sin la señal (%)"],
        var_name="Grupo", value_name="churn",
    )
    datos["Grupo"] = datos["Grupo"].map({"Churn con la señal (%)": "Con la señal", "Churn sin la señal (%)": "Sin la señal"})
    datos["Señal"] = "<b>" + datos["Tipo"] + "</b><br>" + datos["Señal"].map(NOMBRE_CORTO)
    orden = ("<b>" + tabla["Tipo"] + "</b><br>" + tabla["Señal"].map(NOMBRE_CORTO)).tolist()
    fig = px.bar(
        datos, x="churn", y="Señal", color="Grupo", orientation="h", barmode="group", text_auto=".1f",
        title="Churn a 60 días con y sin cada señal",
        labels={"churn": "Churn a 60 días (%)", "Señal": ""},
        category_orders={"Señal": orden, "Grupo": ["Con la señal", "Sin la señal"]},
        color_discrete_map={"Con la señal": COLOR_CON, "Sin la señal": COLOR_SIN},
    )
    fig.update_layout(legend=dict(title_text="", orientation="h", yanchor="bottom", y=1.0, x=0))
    fig.update_yaxes(automargin=True)
    return fig


def figura_uso_canal(df):
    datos = df[df["churn_60d"].notna() & df["estado_wa"].isin(["Conectado", "Desconectado"])]
    if datos.empty:
        return None
    datos = datos.groupby(["nivel_adopcion", "estado_wa"], as_index=False).agg(
        churn=("churn_60d", "mean"), casos=("account_id", "size")
    )
    datos["churn_%"] = datos["churn"] * 100
    datos["nivel_adopcion"] = datos["nivel_adopcion"].map(NIVEL_CORTO)
    fig = px.bar(
        datos, x="nivel_adopcion", y="churn_%", color="estado_wa", barmode="group", text_auto=".0f",
        title="¿El canal suma algo al uso?",
        labels={"churn_%": "Churn a 60 días (%)", "nivel_adopcion": "Días activos en el mes", "estado_wa": "WhatsApp Web"},
        category_orders={"nivel_adopcion": list(NIVEL_CORTO.values()), "estado_wa": ["Desconectado", "Conectado"]},
        hover_data={"casos": True},
        color_discrete_map={"Desconectado": COLOR_CON, "Conectado": COLOR_SIN},
    )
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0))
    fig.update_xaxes(tickangle=0, automargin=True)
    return fig


@st.cache_data
def cargar(carpeta):
    panel = pd.read_csv(carpeta / "panel_mensual.csv", parse_dates=["mes"])
    perfil = pd.read_csv(carpeta / "perfil_cuentas.csv", parse_dates=["fecha_inicio", "fecha_baja"])
    cancelaciones = pd.read_csv(carpeta / "cancelaciones.csv", parse_dates=["fecha"])
    eventos = pd.read_csv(carpeta / "historial_canales_eventos.csv", parse_dates=["fecha_hora"])

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

    # Otras señales de la Evidencia 4: uso bajo sostenido, mora y soporte
    por_cuenta = panel.groupby("account_id")
    dias_previo = por_cuenta["prop_dias_activos"].shift(1)
    panel["uso_bajo_2m"] = np.where(
        panel["ventana_completa"], ((panel["prop_dias_activos"] < 0.5) & (dias_previo < 0.5)).astype(float), np.nan
    )
    panel["mora"] = panel["en_morosidad"].astype(float)
    tickets_3m = (
        panel["n_tickets_soporte"] + por_cuenta["n_tickets_soporte"].shift(1) + por_cuenta["n_tickets_soporte"].shift(2)
    )
    panel["tickets_3m"] = np.where(panel["ventana_completa"], (tickets_3m > 0).astype(float), np.nan)

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

    # Canal: estado de WhatsApp Web al cierre de cada mes
    base = base.merge(estado_whatsapp(eventos, base[["account_id", "corte"]]), on=["account_id", "corte"], how="left")
    base["wa_desconectado"] = base["estado_wa"].map({"Desconectado": 1.0, "Conectado": 0.0})

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


@st.cache_data
def cargar_scores(carpeta):
    """Score de riesgo del modelo de la Evidencia 4 para cada cuenta activa al 31-oct-2026.
    No se entrena nada aquí: el notebook de la Evidencia 5 entrena el modelo (Extra Trees calibrado)
    y los perfiles (K-Means) y exporta el resultado a datos/scores_modelo_hoy.csv.
    Si el archivo no existe, el tablero funciona igual y solo oculta esta sección."""
    ruta = carpeta / "scores_modelo_hoy.csv"
    if not ruta.exists():
        return None
    scores = pd.read_csv(ruta, parse_dates=["corte"])
    # En el archivo, "segmento" es el perfil de K-Means; aquí se llama "perfil" para no
    # confundirlo con el segmento de negocio (B&L, WAPI...) que usan los filtros.
    return scores.rename(columns={"segmento": "perfil", "variacion_chats_%": "variacion_chats"})


base, antes_baja, motivos = cargar(CARPETA_DATOS)
scores = cargar_scores(CARPETA_DATOS)

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
    "**¿La baja adopción de funcionalidades y canales anticipa la cancelación?** Comparamos cuántas cuentas "
    "cancelan en los 60 días siguientes al cierre de cada mes, según cómo venían usando LeadSales y si "
    "tenían su canal conectado."
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

# --- Comparación de señales: ¿qué tipo de baja adopción anticipa la cancelación? ---
st.subheader("¿Qué señal anticipa mejor la cancelación?")
st.caption(
    "Comparamos señales de **uso** de la plataforma, del **canal** (WhatsApp Web) y de **contexto** (mora y soporte). "
    "Cada par de barras compara el churn a 60 días de las cuentas que tenían la señal al cierre del mes "
    "contra las que no la tenían."
)

if con_desenlace.empty:
    st.info("Sin desenlace en el periodo elegido.")
else:
    tabla_senales = comparar_senales(filtrados)
    if tabla_senales.empty:
        st.info("No hay suficientes cuentas con esos filtros para comparar las señales.")
    else:
        col_senales, col_canal = st.columns(2)
        col_senales.plotly_chart(figura_senales(tabla_senales), width="stretch")
        fig_canal = figura_uso_canal(filtrados)
        if fig_canal is None:
            col_canal.info("No hay cuentas con WhatsApp Web registrado con esos filtros.")
        else:
            col_canal.plotly_chart(fig_canal, width="stretch")
        st.dataframe(tabla_senales, width="stretch", hide_index=True)
        st.caption(
            "Casos = cuenta y mes de corte. El canal solo considera cuentas con WhatsApp Web conectado o "
            "desconectado al cierre; las que no usan WhatsApp Web (por ejemplo, las de API) quedan fuera."
        )

st.divider()

# --- ¿Quién está en riesgo hoy? Score del modelo de la Evidencia 4 ---
st.subheader("¿Quién está en riesgo hoy? Score del modelo")
if scores is None:
    st.info(
        "Falta el archivo datos/scores_modelo_hoy.csv. Ejecuta el notebook de la Evidencia 5 "
        "para generarlo y vuelve a cargar el tablero."
    )
else:
    st.caption(
        "Probabilidad de cancelar en los 60 días siguientes al **31-oct-2026**, según el modelo Extra Trees "
        "calibrado de la Evidencia 4. Usa los filtros de plan, segmento e industria; el periodo no aplica "
        "porque el score es la foto de hoy. En la prueba de agosto, el **decil 1** (10 % de cuentas con mayor "
        "score) canceló **2.3 veces** más que el promedio."
    )
    # Plan, segmento e industria vienen del corte de octubre del tablero
    datos_corte = base.loc[base["corte"] == scores["corte"].max(), ["account_id", "segmento", "industria"]]
    hoy = scores.merge(datos_corte, on="account_id", how="left")
    hoy = hoy[hoy["plan"].isin(planes) & hoy["segmento"].isin(segmentos) & hoy["industria"].isin(industrias)]

    if hoy.empty:
        st.warning("No hay cuentas con score para esos filtros. Amplía la selección.")
    else:
        decil_1 = hoy[hoy["decil_riesgo"] == 1]
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Cuentas evaluadas hoy", f"{len(hoy):,}")
        k2.metric("Prioridad: decil 1", f"{len(decil_1):,}", help="Cuentas en el 10 % de mayor score de toda la cartera")
        k3.metric(
            "Sobre el umbral del modelo",
            f"{(hoy['score'] >= UMBRAL_MODELO).sum():,}",
            help=f"Score ≥ {UMBRAL_MODELO:.1%}: umbral elegido con F2 en la Evidencia 4 (prioriza no perder cancelaciones)",
        )
        k4.metric(
            "Decil 1 con WhatsApp Web desconectado",
            f"{(decil_1['estado_wa'] == 'Desconectado').sum():,}",
            help="Revisar primero el canal: puede ser un problema técnico con solución rápida",
        )

        col_perfil, col_accion = st.columns([3, 2])
        por_perfil = (
            hoy.groupby("perfil")
            .agg(cuentas=("account_id", "size"), decil_1=("decil_riesgo", lambda d: (d == 1).sum()))
            .reindex(list(COLOR_PERFIL))
            .dropna()
            .reset_index()
        )
        col_perfil.plotly_chart(
            px.bar(
                por_perfil, x="decil_1", y="perfil", color="perfil", orientation="h", text_auto=True,
                title="Cuentas del decil 1 por perfil de adopción (K-Means)",
                labels={"decil_1": "Cuentas en el decil 1", "perfil": ""},
                hover_data={"cuentas": True},
                category_orders={"perfil": list(COLOR_PERFIL)},
                color_discrete_map=COLOR_PERFIL,
            ).update_layout(showlegend=False),
            width="stretch",
        )
        col_accion.markdown("**Qué hacer con cada perfil**")
        for perfil, accion in ACCION_PERFIL.items():
            col_accion.markdown(f"- **{perfil}:** {accion}")

        perfiles_elegidos = st.multiselect(
            "Ver perfiles", options=list(COLOR_PERFIL), default=list(COLOR_PERFIL), key="perfiles_score"
        )
        lista = hoy[hoy["perfil"].isin(perfiles_elegidos)].sort_values(
            ["score", "variacion_chats"], ascending=[False, True]
        )
        lista_score = pd.DataFrame({
            "Account ID": lista["account_id"],
            "Plan": lista["plan"],
            "Segmento": lista["segmento"],
            "Industria": lista["industria"],
            "Perfil": lista["perfil"],
            "Score (%)": (lista["score"] * 100).round(1),
            "Decil": lista["decil_riesgo"],
            "Variación de chats (%)": lista["variacion_chats"].round(0),
            "Días activos (%)": (lista["prop_dias_activos"] * 100).round(0),
            "WhatsApp Web": lista["estado_wa"],
        })
        st.caption(f"{len(lista_score):,} cuentas, de mayor a menor score. Empates: primero la mayor caída de chats.")
        st.dataframe(
            lista_score,
            width="stretch",
            hide_index=True,
            column_config={
                "Score (%)": st.column_config.ProgressColumn(
                    "Score (%)", min_value=0, max_value=float(max(35, lista_score["Score (%)"].max())), format="%.1f"
                ),
            },
        )
        st.download_button(
            "Descargar lista de revisión (CSV)",
            data=lista_score.to_csv(index=False).encode("utf-8"),
            file_name="lista_revision_score_2026-10.csv",
            mime="text/csv",
            type="primary",
        )
        st.caption(
            "El score ordena a quién llamar primero; el perfil dice qué ofrecer. Es una probabilidad, no una "
            "certeza: muchas cuentas del decil 1 no cancelan."
        )

st.divider()

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
                color_discrete_map={"Con caída ≥50%": COLOR_CON, "Sin caída": COLOR_SIN, "No medible": NEUTRO},
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

**Las señales de adopción**
- **Caída ≥50% de chats:** los chats del mes son la mitad o menos del promedio de los dos meses
  anteriores. Si ese promedio es 0 o falta un mes, la caída no se puede medir (no se toma como 0).
- **Días activos:** proporción de días del mes en los que la cuenta usó la plataforma.
- **WhatsApp Web desconectado:** el canal estaba desconectado (por más de 24 h) al cierre del mes.

**Qué encontramos.** La baja adopción **sí anticipa la cancelación**, tanto en el **uso** como en el
**canal**. Las cuentas con caída de chats ≥50% o con pocos días activos cancelan unas 3 veces más, y lo
mismo pasa con las que tienen WhatsApp Web desconectado al cierre del mes. El patrón se repite en los
4 meses con desenlace y se mantiene incluso entre cuentas con uso alto y estable. En el modelo de la
Evidencia 4 (que medía la conexión de otra forma, como % del tiempo conectado en 3 meses), el canal no
mejoró la predicción de forma consistente una vez que ya se conocía el uso. Por eso lo usamos como señal
complementaria y de diagnóstico (¿la caída es un problema técnico?). La **mora** duplica el riesgo, y
abrir **tickets de soporte** se asocia con *menos* churn: quien pide ayuda sigue comprometido.

**Score del modelo.** La sección "¿Quién está en riesgo hoy?" usa el modelo de la Evidencia 4
(Extra Trees calibrado) para estimar la probabilidad de cancelar en los 60 días siguientes al 31-oct-2026,
y los perfiles de adopción de K-Means (descenso de actividad, uso muy bajo o nulo, uso estable) para
sugerir la acción. El notebook de la Evidencia 5 entrena ambos modelos y genera `datos/scores_modelo_hoy.csv`.

**Limitaciones**
- Es una **asociación**, no una causa: una caída no significa que la cuenta se vaya a ir.
- Septiembre y octubre todavía no tienen desenlace a 60 días.
- Solo se usa WhatsApp Web: Instagram, Facebook y la API tienen desconexiones faltantes y borrados masivos.
  En julio hubo una migración técnica que generó desconexiones que no son decisión del cliente.
- Solo se incluyen cuentas con al menos 3 meses seguidos de historial; las cuentas nuevas (onboarding)
  necesitan otro seguimiento.
"""
    )
