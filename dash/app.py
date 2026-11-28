"""
LeadSales · Monitor de adopción y riesgo de churn, versión Dash (Equipo Teki)

Laboratorio 11: el mismo tablero de Streamlit (app/app.py), construido como un
árbol de componentes.
Laboratorio 12: los filtros se conectan con un solo callback que actualiza
indicadores, gráficas y tablas, y muestra un aviso si la selección queda vacía.
Evidencia 5: colores alineados con el prototipo de Figma (paleta de LeadSales) y
sección "¿Quién está en riesgo hoy?" con el score del modelo de la Evidencia 4
(lo genera el notebook de la Evidencia 5 en datos/scores_modelo_hoy.csv).

Se ejecuta desde la raíz del repositorio:
    python dash/app.py
y se abre en http://localhost:8050
"""

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dash_table, dcc, html

# =============================================================================
# 1. Estilos reutilizables (se definen una sola vez)
# =============================================================================
# Paleta del prototipo de Figma (Evidencia 5): sale del azul de LeadSales con la teoría del color
#   60 % fondo neutro · 30 % marca · 10 % acento (complementario, solo para acciones)
#   rojo, naranja y verde solo con su significado (riesgo, advertencia, éxito)
FONDO = "#F5F6FA"        # 60 % · fondo de la página
SUPERFICIE = "#FFFFFF"   # 60 % · tarjetas y barra lateral
MARCA = "#4145E3"        # 30 % · logo, menú activo y serie de referencia en las gráficas
MARCA_TINTE = "#E4E5FB"  # tinte de la marca (fondos suaves)
ACENTO = "#E3DE41"       # 10 % · complementario de la marca: solo botones de acción, con texto oscuro
TINTA = "#202B37"        # texto principal (13.3:1 sobre el fondo)
GRIS = "#637083"         # texto secundario (5.0:1 sobre blanco)
BORDE = "#E1E4EC"
ROJO = "#DC2626"         # semántico · riesgo
ADVERTENCIA = "#C2410C"  # semántico · atención (pasa WCAG con texto blanco: 5.2:1)
NEUTRO = "#C5C9D4"       # casos que no se pueden medir
GRIS_BARRA = MARCA       # la serie "sin la señal" ahora es azul de marca, como en Figma
FUENTE = "Inter, Segoe UI, Helvetica, Arial, sans-serif"

# Perfiles de adopción del K-Means de la Evidencia 4: un color por perfil en todo el tablero
COLOR_PERFIL = {
    "Descenso de actividad": ROJO,
    "Uso muy bajo o nulo": ADVERTENCIA,
    "Uso estable": MARCA,
}
ACCION_PERFIL = {
    "Descenso de actividad": "Primera prioridad: llamada de diagnóstico, revisar si WhatsApp Web está desconectado y ofrecer capacitación.",
    "Uso muy bajo o nulo": "Reactivación o ajuste de plan antes de su renovación.",
    "Uso estable": "Seguimiento normal; atender solo si entra al decil 1 o desconecta WhatsApp Web.",
}
UMBRAL_MODELO = 0.095  # umbral del modelo elegido con F2 en la Evidencia 4

ESTILO_PAGINA = {
    "fontFamily": FUENTE,
    "backgroundColor": FONDO,
    "display": "flex",
    "minHeight": "100vh",
    "margin": "-8px",  # quita el margen que el navegador pone por defecto
}
ESTILO_BARRA_LATERAL = {
    "width": "240px",
    "flexShrink": "0",
    "backgroundColor": SUPERFICIE,
    "padding": "24px 16px",
    "borderRight": f"1px solid {BORDE}",
}
ESTILO_CONTENIDO = {"flex": "1", "padding": "24px", "minWidth": "0"}
ESTILO_FILA = {"display": "flex", "gap": "16px", "marginBottom": "16px"}
ESTILO_TARJETA = {
    "flex": "1",
    "backgroundColor": SUPERFICIE,
    "borderRadius": "12px",
    "padding": "16px",
    "border": f"1px solid {BORDE}",
}
ESTILO_ETIQUETA = {"fontWeight": "600", "fontSize": "13px", "color": TINTA,
                   "display": "block", "marginTop": "14px", "marginBottom": "4px"}
ESTILO_TITULO_SECCION = {"fontSize": "12px", "fontWeight": "700", "color": GRIS,
                         "letterSpacing": "0.5px", "margin": "24px 0 4px 0"}
ESTILO_MENU = {"padding": "8px 10px", "borderRadius": "6px", "color": TINTA, "fontSize": "14px"}
ESTILO_MENU_ACTIVO = {**ESTILO_MENU, "backgroundColor": MARCA, "color": "white", "fontWeight": "600"}

# =============================================================================
# 2. Datos (misma preparación que la versión de Streamlit)
# =============================================================================
CARPETA_DATOS = Path(__file__).parent.parent / "datos"

CORTE_DATOS = pd.Timestamp("2026-10-31")
HORIZONTE_DIAS = 60
PRIMER_CORTE = pd.Timestamp("2026-05-01")

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

ORDEN_NIVELES = ["Baja (<25% de días)", "Media (25–75%)", "Alta (>75%)"]


def etiqueta_mes(fecha):
    return f"{MESES_ES[fecha.month]} {fecha.year}"


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
        color_discrete_map={"Con la señal": ROJO, "Sin la señal": GRIS_BARRA},
    )
    fig.update_layout(legend=dict(title_text="", orientation="h", yanchor="bottom", y=1.0, x=0))
    fig.update_yaxes(automargin=True)
    return ajustar(fig)


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
        color_discrete_map={"Desconectado": ROJO, "Conectado": GRIS_BARRA},
    )
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0))
    fig.update_xaxes(tickangle=0, automargin=True)
    return ajustar(fig)


def cargar(carpeta):
    """Lee los tres CSV y arma las tablas del tablero.
    En Dash no hace falta caché: esto corre una sola vez, al arrancar la aplicación."""
    panel = pd.read_csv(carpeta / "panel_mensual.csv", parse_dates=["mes"])
    perfil = pd.read_csv(carpeta / "perfil_cuentas.csv", parse_dates=["fecha_inicio", "fecha_baja"])
    cancelaciones = pd.read_csv(carpeta / "cancelaciones.csv", parse_dates=["fecha"])
    eventos = pd.read_csv(carpeta / "historial_canales_eventos.csv", parse_dates=["fecha_hora"])

    panel = panel.sort_values(["account_id", "mes"]).reset_index(drop=True)
    panel["industria"] = panel["industria"].replace(INDUSTRIAS).fillna("Otra / no declarada")
    panel = panel.merge(perfil[["account_id", "fecha_inicio", "fecha_baja"]], on="account_id", how="left")

    # Caída de chats: chats del mes contra el promedio de los dos meses anteriores
    por_cuenta = panel.groupby("account_id")
    previo_1, previo_2 = por_cuenta["mes"].shift(1), por_cuenta["mes"].shift(2)
    consecutivos = (previo_1 == panel["mes"] - pd.DateOffset(months=1)) & (
        previo_2 == panel["mes"] - pd.DateOffset(months=2)
    )
    previos_activos = (por_cuenta["estado_en_mes"].shift(1) == "activa") & (
        por_cuenta["estado_en_mes"].shift(2) == "activa"
    )
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
        panel["prop_dias_activos"], bins=[-0.01, 0.25, 0.75, 1.01], labels=ORDEN_NIVELES
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

    # Base: cuentas activas al cierre de cada mes, con 3 meses de historial
    base = panel[
        (panel["estado_en_mes"] == "activa") & panel["ventana_completa"] & (panel["mes"] >= PRIMER_CORTE)
    ].copy()
    base["corte"] = base["mes"] + pd.offsets.MonthEnd(0)
    base = base[base["fecha_baja"].isna() | (base["fecha_baja"] > base["corte"])]

    # Desenlace: ¿canceló en los 60 días siguientes al corte?
    fin_ventana = base["corte"] + pd.Timedelta(days=HORIZONTE_DIAS)
    cancelo = (base["fecha_baja"] > base["corte"]) & (base["fecha_baja"] <= fin_ventana)
    base["churn_60d"] = np.where(fin_ventana <= CORTE_DATOS, cancelo.astype(float), np.nan)

    # Canal: estado de WhatsApp Web al cierre de cada mes
    base = base.merge(estado_whatsapp(eventos, base[["account_id", "corte"]]), on=["account_id", "corte"], how="left")
    base["wa_desconectado"] = base["estado_wa"].map({"Desconectado": 1.0, "Conectado": 0.0})

    # Actividad en los meses previos a la baja
    con_baja = panel[panel["fecha_baja"].notna() & panel["estado_en_mes"].isin(["activa", "baja_este_mes"])].copy()
    mes_baja = con_baja["fecha_baja"].dt.to_period("M")
    con_baja["meses_antes"] = (
        (mes_baja.dt.year - con_baja["mes"].dt.year) * 12 + (mes_baja.dt.month - con_baja["mes"].dt.month)
    )
    antes_baja = con_baja[con_baja["meses_antes"].between(0, 4)]

    # Motivo de cancelación: la última respuesta de cada cuenta
    motivos = (
        cancelaciones.sort_values("fecha")
        .drop_duplicates("account_id", keep="last")[["account_id", "motivo_normalizado"]]
    )
    motivos["motivo"] = motivos["motivo_normalizado"].map(NOMBRES_MOTIVOS).fillna("Otro motivo")

    return base, antes_baja, motivos


base, antes_baja, motivos = cargar(CARPETA_DATOS)
CORTES = sorted(base["corte"].unique())

TODAS_INDUSTRIAS = sorted(base["industria"].unique())

TEXTO_AYUDA = """
**Qué responde este tablero.** Si la baja adopción anticipa la cancelación. Para cada cuenta activa al
cierre de un mes revisamos cómo venía usando LeadSales y si canceló en los **60 días siguientes**.

**Las señales de adopción**
- **Caída ≥50% de chats:** los chats del mes son la mitad o menos del promedio de los dos meses anteriores.
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

**Limitaciones**
- Es una **asociación**, no una causa: una caída no significa que la cuenta se vaya a ir.
- Septiembre y octubre todavía no tienen desenlace a 60 días.
- Solo se usa WhatsApp Web: Instagram, Facebook y la API tienen desconexiones faltantes y borrados masivos.
  En julio hubo una migración técnica que generó desconexiones que no son decisión del cliente.
- Solo se incluyen cuentas con al menos 3 meses seguidos de historial.

**Score del modelo.** La sección "¿Quién está en riesgo hoy?" usa el modelo de la Evidencia 4 (Extra Trees
calibrado) para estimar la probabilidad de cancelar en los 60 días siguientes al 31-oct-2026, y los perfiles
de adopción de K-Means para sugerir la acción. El notebook de la Evidencia 5 entrena ambos modelos y genera
`datos/scores_modelo_hoy.csv`.
"""

# =============================================================================
# 3. Cálculos: indicadores, figuras y tablas
#    Ya no se calculan al arrancar: el callback (sección 6) los llama con los
#    datos filtrados cada vez que se mueve un filtro.
# =============================================================================

COLUMNAS_SENALES = ["Tipo", "Señal", "Casos con la señal (%)", "Churn con la señal (%)",
                    "Churn sin la señal (%)", "Veces más"]
COLUMNAS_RIESGO = ["Account ID", "Plan", "Segmento", "Industria", "Chats del mes",
                   "Chats promedio (2 meses previos)", "Variación (%)", "Días activos (%)",
                   "Desenlace a 60 días"]


def ajustar(fig):
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10), plot_bgcolor=SUPERFICIE, paper_bgcolor=SUPERFICIE,
                      font_family=FUENTE, font_color=TINTA,
                      title_font_size=15, title_font_color=TINTA)
    fig.update_xaxes(automargin=True, gridcolor=BORDE, zerolinecolor=BORDE)
    fig.update_yaxes(automargin=True, gridcolor=BORDE, zerolinecolor=BORDE)
    return fig


def figura_vacia(titulo):
    """Figura sin datos, para cuando los filtros no dejan nada que graficar."""
    fig = px.scatter(title=titulo)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return ajustar(fig)


def registros(df):
    """Convierte una tabla a filas para DataTable (los vacíos se mandan como None)."""
    return df.astype(object).where(df.notna(), None).to_dict("records")


def indicadores(df):
    con_desenlace = df[df["churn_60d"].notna()]
    ultimo = df["corte"].max()
    resultado = {
        "activas": f"{df.loc[df['corte'] == ultimo, 'account_id'].nunique():,}",
        "activas_nota": f"Al cierre de {etiqueta_mes(ultimo)}",
        "caida": f"{df['caida_50'].mean() * 100:.1f}%" if df["caida_50"].notna().any() else "Sin dato",
        "churn": "Sin desenlace",
        "veces": "Sin desenlace",
        "veces_nota": "Elige algún mes entre mayo y agosto",
    }
    if con_desenlace.empty:
        return resultado
    resultado["churn"] = f"{con_desenlace['churn_60d'].mean() * 100:.1f}%"
    churn_con = con_desenlace.loc[con_desenlace["caida_50"] == 1, "churn_60d"].mean() * 100
    churn_sin = con_desenlace.loc[con_desenlace["caida_50"] == 0, "churn_60d"].mean() * 100
    if pd.notna(churn_con) and pd.notna(churn_sin) and churn_sin > 0:
        resultado["veces"] = f"{churn_con / churn_sin:.1f}× más"
        resultado["veces_nota"] = f"{churn_con:.0f}% de churn con caída vs {churn_sin:.0f}% sin caída"
    else:
        resultado["veces"] = "Sin dato"
        resultado["veces_nota"] = "No hay suficientes cuentas con y sin caída"
    return resultado


def figura_por_corte(df):
    titulo = "Churn a 60 días: con caída de chats vs sin caída"
    con_desenlace = df[df["churn_60d"].notna()].dropna(subset=["caida_50"])
    if con_desenlace.empty:
        return figura_vacia(titulo)
    datos = con_desenlace.groupby(["corte", "caida_50"], as_index=False)["churn_60d"].mean()
    datos["churn_%"] = datos["churn_60d"] * 100
    datos["Mes de corte"] = datos["corte"].map(etiqueta_mes)
    datos["Actividad"] = datos["caida_50"].map({1.0: "Con caída ≥50%", 0.0: "Sin caída"})
    fig = px.bar(
        datos, x="Mes de corte", y="churn_%", color="Actividad", barmode="group", text_auto=".0f",
        title=titulo,
        labels={"churn_%": "Churn a 60 días (%)"},
        color_discrete_map={"Con caída ≥50%": ROJO, "Sin caída": GRIS_BARRA},
    )
    fig.add_hline(y=con_desenlace["churn_60d"].mean() * 100, line_dash="dot", annotation_text="Promedio")
    return ajustar(fig)


def figura_por_nivel(df):
    titulo = "Churn a 60 días según los días activos del mes"
    con_desenlace = df[df["churn_60d"].notna()]
    if con_desenlace.empty:
        return figura_vacia(titulo)
    datos = con_desenlace.groupby("nivel_adopcion", as_index=False).agg(
        churn=("churn_60d", "mean"), cuentas=("account_id", "size")
    )
    datos["churn_%"] = datos["churn"] * 100
    fig = px.bar(
        datos, x="churn_%", y="nivel_adopcion", orientation="h", text_auto=".1f",
        title=titulo,
        labels={"churn_%": "Churn a 60 días (%)", "nivel_adopcion": "Días activos en el mes"},
        category_orders={"nivel_adopcion": ORDEN_NIVELES}, hover_data={"cuentas": True},
        color_discrete_sequence=[GRIS_BARRA],
    )
    return ajustar(fig)


def figura_antes_baja(bajas, referencia):
    titulo = "¿El uso cae antes de cancelar? Días activos (mediana) de quienes cancelaron"
    if bajas.empty:
        return figura_vacia(titulo)
    datos = bajas.groupby("meses_antes", as_index=False).agg(
        dias_activos=("prop_dias_activos", "median"), cuentas=("account_id", "nunique")
    )
    datos["dias_activos"] = datos["dias_activos"] * 100
    datos["Mes"] = datos["meses_antes"].map(
        lambda m: "Mes de la baja" if m == 0 else "1 mes antes" if m == 1 else f"{m} meses antes"
    )
    datos = datos.sort_values("meses_antes", ascending=False)
    fig = px.line(
        datos, x="Mes", y="dias_activos", markers=True,
        title=titulo,
        labels={"dias_activos": "Días activos del mes (%)", "Mes": ""},
        hover_data={"cuentas": True}, color_discrete_sequence=[ROJO],
    )
    if pd.notna(referencia):
        fig.add_hline(y=referencia, line_dash="dot", annotation_text="Cuentas que se quedan")
    fig.update_yaxes(range=[0, 105])
    return ajustar(fig)


def figura_motivos(df):
    titulo = "¿Qué dijeron al cancelar?"
    canceladas = (
        df[df["churn_60d"] == 1].sort_values("corte").drop_duplicates("account_id", keep="last")
        .merge(motivos, on="account_id", how="inner")
    )
    if canceladas.empty:
        return figura_vacia(titulo)
    canceladas["Actividad al corte"] = canceladas["caida_50"].map(
        {1.0: "Con caída ≥50%", 0.0: "Sin caída"}
    ).fillna("No medible")
    datos = canceladas.groupby(["motivo", "Actividad al corte"], as_index=False).size()
    fig = px.bar(
        datos, x="size", y="motivo", color="Actividad al corte", orientation="h",
        title=titulo, labels={"size": "Cuentas", "motivo": ""},
        color_discrete_map={"Con caída ≥50%": ROJO, "Sin caída": GRIS_BARRA, "No medible": NEUTRO},
    )
    return ajustar(fig)


def tabla_en_riesgo(df):
    ultimo = df["corte"].max()
    en_riesgo = df[(df["corte"] == ultimo) & (df["caida_50"] == 1)].sort_values("variacion_chats")
    return pd.DataFrame({
        "Account ID": en_riesgo["account_id"],
        "Plan": en_riesgo["plan"],
        "Segmento": en_riesgo["segmento"],
        "Industria": en_riesgo["industria"],
        "Chats del mes": en_riesgo["n_chats"],
        "Chats promedio (2 meses previos)": en_riesgo["chats_base"].round(0),
        "Variación (%)": en_riesgo["variacion_chats"].round(0),
        "Días activos (%)": (en_riesgo["prop_dias_activos"] * 100).round(0),
        "Desenlace a 60 días": en_riesgo["churn_60d"].map({1.0: "Canceló", 0.0: "Sigue activa"})
        .fillna("Aún sin desenlace"),
    }, columns=COLUMNAS_RIESGO)


# --- Score del modelo de la Evidencia 4 (la foto de hoy: 31-oct-2026) ---
COLUMNAS_SCORE = ["Account ID", "Plan", "Segmento", "Industria", "Perfil", "Score (%)", "Decil",
                  "Variación de chats (%)", "Días activos (%)", "WhatsApp Web"]


def cargar_scores(carpeta):
    """Score de riesgo (Extra Trees calibrado) y perfil de adopción (K-Means) de cada cuenta activa
    al 31-oct-2026. No se entrena nada aquí: el notebook de la Evidencia 5 entrena los modelos y
    exporta datos/scores_modelo_hoy.csv. Si el archivo no existe, la sección queda vacía con un aviso."""
    ruta = carpeta / "scores_modelo_hoy.csv"
    if not ruta.exists():
        return None
    scores = pd.read_csv(ruta, parse_dates=["corte"])
    # En el archivo, "segmento" es el perfil de K-Means; aquí se llama "perfil" para no confundirlo
    # con el segmento de negocio que usan los filtros. Plan, segmento e industria salen del corte de octubre.
    scores = scores.rename(columns={"segmento": "perfil", "variacion_chats_%": "variacion_chats"})
    datos_corte = base.loc[base["corte"] == scores["corte"].max(), ["account_id", "segmento", "industria"]]
    return scores.merge(datos_corte, on="account_id", how="left")


SCORES = cargar_scores(CARPETA_DATOS)


def indicadores_score(hoy):
    decil_1 = hoy[hoy["decil_riesgo"] == 1]
    return (
        f"{len(hoy):,}",
        f"{len(decil_1):,}",
        f"{(hoy['score'] >= UMBRAL_MODELO).sum():,}",
        f"{(decil_1['estado_wa'] == 'Desconectado').sum():,}",
    )


def figura_score_perfil(hoy):
    titulo = "Cuentas del decil 1 por perfil de adopción (K-Means)"
    if hoy.empty:
        return figura_vacia(titulo)
    datos = (
        hoy.groupby("perfil")
        .agg(cuentas=("account_id", "size"), decil_1=("decil_riesgo", lambda d: (d == 1).sum()))
        .reindex(list(COLOR_PERFIL)).dropna().reset_index()
    )
    fig = px.bar(
        datos, x="decil_1", y="perfil", color="perfil", orientation="h", text_auto=True,
        title=titulo, labels={"decil_1": "Cuentas en el decil 1", "perfil": ""},
        hover_data={"cuentas": True}, category_orders={"perfil": list(COLOR_PERFIL)},
        color_discrete_map=COLOR_PERFIL,
    )
    fig.update_layout(showlegend=False)
    return ajustar(fig)


def tabla_score(hoy, perfiles):
    lista = hoy[hoy["perfil"].isin(perfiles)].sort_values(["score", "variacion_chats"], ascending=[False, True])
    return pd.DataFrame({
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
    }, columns=COLUMNAS_SCORE)


# =============================================================================
# 4. Pedazos de árbol reutilizables
# =============================================================================
# Aviso como en la Pantalla 6 de Figma: fondo blanco, borde naranja de advertencia y texto oscuro
ESTILO_AVISO = {"backgroundColor": SUPERFICIE, "color": TINTA, "padding": "12px 16px",
                "border": f"1.5px solid {ADVERTENCIA}", "borderLeft": f"6px solid {ADVERTENCIA}",
                "borderRadius": "8px", "marginBottom": "16px", "fontWeight": "600"}
ESTILO_NOTA_TARJETA = {"fontSize": "12px", "color": GRIS, "marginTop": "4px"}


def tarjeta(titulo, id_valor, nota=None, nota_dinamica=False, alerta=False, ancho="1"):
    """Tarjeta de indicador SIN valor fijo: el callback llena el elemento con id=id_valor.
    nota_dinamica=True deja también la nota vacía, con id=f"{id_valor}-nota", para el callback.
    alerta=True la marca en rojo con un ícono, como en el wireframe."""
    color = ROJO if alerta else TINTA
    encabezado = [titulo, html.Span(" ⚠", style={"color": ROJO})] if alerta else [titulo]
    hijos = [
        html.Div(encabezado, style={"fontSize": "13px", "color": GRIS}),
        html.Div(id=id_valor, style={"fontSize": "26px", "fontWeight": "600", "color": color}),
    ]
    if nota_dinamica:
        hijos.append(html.Div(id=f"{id_valor}-nota", style=ESTILO_NOTA_TARJETA))
    elif nota:
        hijos.append(html.Div(nota, style=ESTILO_NOTA_TARJETA))
    estilo = {**ESTILO_TARJETA, "flex": ancho}
    if alerta:
        estilo["borderTop"] = f"3px solid {ROJO}"
    return html.Div(hijos, style=estilo)


def opcion_menu(texto, activa=False):
    return html.Div(texto, style=ESTILO_MENU_ACTIVO if activa else ESTILO_MENU)


def grafica(id_grafica, alto="380px"):
    """Gráfica SIN figura fija: el callback la llena."""
    return html.Div(dcc.Graph(id=id_grafica, style={"height": alto}), style=ESTILO_TARJETA)


def tabla(id_tabla, columnas, **extra):
    return dash_table.DataTable(
        id=id_tabla,
        columns=[{"name": c, "id": c} for c in columnas],
        data=[],
        style_table={"overflowX": "auto"},
        style_header={"backgroundColor": TINTA, "color": "white", "fontWeight": "600"},
        style_cell={"fontFamily": FUENTE, "fontSize": "13px", "color": TINTA,
                    "padding": "6px", "textAlign": "left", "border": f"1px solid {BORDE}"},
        **extra,
    )


# =============================================================================
# 5. Layout: el árbol de componentes
# =============================================================================
app = Dash(__name__, title="LeadSales | Adopción y riesgo de churn")

barra_lateral = html.Div([
    html.Div("leadsales", style={"fontSize": "24px", "fontWeight": "700", "color": MARCA}),
    html.Div("Adoption & Churn Monitor", style={"fontSize": "13px", "color": GRIS, "marginBottom": "16px"}),

    # --- Navegación entre pantallas (como en el wireframe) ---
    opcion_menu("Dashboard principal", activa=True),
    opcion_menu("Explorador de cuentas"),
    opcion_menu("Perfil 360"),
    opcion_menu("Análisis de adopción"),

    # --- Filtros: cada uno es un Input del callback ---
    html.Div("FILTROS GLOBALES", style=ESTILO_TITULO_SECCION),

    html.Label("Periodo (mes de corte)", style=ESTILO_ETIQUETA),
    dcc.RangeSlider(
        id="filtro-periodo",
        min=0,
        max=len(CORTES) - 1,
        step=1,
        value=[0, len(CORTES) - 1],
        marks={i: MESES_ES[c.month] for i, c in enumerate(CORTES)},
    ),

    html.Label("Plan", style=ESTILO_ETIQUETA),
    dcc.Dropdown(
        id="filtro-plan",
        options=sorted(base["plan"].dropna().unique()),
        value=sorted(base["plan"].dropna().unique()),
        multi=True,
    ),

    html.Label("Segmento", style=ESTILO_ETIQUETA),
    dcc.Dropdown(
        id="filtro-segmento",
        options=sorted(base["segmento"].dropna().unique()),
        value=sorted(base["segmento"].dropna().unique()),
        multi=True,
    ),

    html.Label("Industria", style=ESTILO_ETIQUETA),
    dcc.Dropdown(
        id="filtro-industria",
        options=TODAS_INDUSTRIAS,
        value=[],
        multi=True,
        placeholder="Todas las industrias",
    ),
    html.Div("Deja Industria vacía para ver todas.", style={"fontSize": "11px", "color": GRIS, "marginTop": "4px"}),
], style=ESTILO_BARRA_LATERAL)

contenido = html.Div([
    # --- Encabezado ---
    html.H2("Monitor de adopción y riesgo de churn", style={"color": TINTA, "marginTop": "0"}),
    html.P([
        html.B("¿La baja adopción de funcionalidades y canales anticipa la cancelación? "),
        "Comparamos cuántas cuentas cancelan en los 60 días siguientes al cierre de cada mes, "
        "según cómo venían usando LeadSales y si tenían su canal conectado.",
    ], style={"color": TINTA}),
    html.P(id="texto-periodo", style={"color": GRIS, "fontSize": "13px"}),

    # --- Aviso: el callback lo llena solo cuando la selección queda vacía ---
    html.Div(id="aviso-vacio"),

    # --- Indicadores (la de riesgo, el doble de ancha y marcada como alerta) ---
    html.Div([
        tarjeta("Cuentas activas", "kpi-activas", nota_dinamica=True),
        tarjeta("Con caída ≥50% de chats", "kpi-caida", nota="Contra el promedio de los 2 meses previos"),
        tarjeta("Churn a 60 días", "kpi-churn", nota="Cancelan en los 60 días siguientes"),
        tarjeta("Riesgo con caída", "kpi-riesgo", nota_dinamica=True, alerta=True, ancho="2"),
    ], style=ESTILO_FILA),

    # --- Dos gráficas lado a lado ---
    html.Div([
        grafica("grafica-corte"),
        grafica("grafica-nivel"),
    ], style=ESTILO_FILA),

    # --- Comparación de señales: ¿qué tipo de baja adopción anticipa la cancelación? ---
    html.H3("¿Qué señal anticipa mejor la cancelación?", style={"color": TINTA, "marginBottom": "4px"}),
    html.P(
        "Comparamos señales de uso de la plataforma, del canal (WhatsApp Web) y de contexto (mora y soporte). "
        "Cada par de barras compara el churn a 60 días de las cuentas que tenían la señal al cierre del mes "
        "contra las que no la tenían.",
        style={"color": GRIS, "fontSize": "13px", "marginTop": "0"},
    ),
    html.Div([
        grafica("grafica-senales", alto="400px"),
        grafica("grafica-uso-canal", alto="400px"),
    ], style=ESTILO_FILA),
    html.Div([
        tabla("tabla-senales", COLUMNAS_SENALES, style_data_conditional=[
            {"if": {"filter_query": "{Veces más} >= 2"}, "color": ROJO, "fontWeight": "600"},
        ]),
        html.P("Casos = cuenta y mes de corte. El canal solo considera cuentas con WhatsApp Web conectado o "
               "desconectado al cierre; las que no usan WhatsApp Web (por ejemplo, las de API) quedan fuera.",
               style={"color": GRIS, "fontSize": "12px", "marginBottom": "0"}),
    ], style={**ESTILO_TARJETA, "marginBottom": "16px"}),

    # --- ¿Quién está en riesgo hoy? Score del modelo de la Evidencia 4 ---
    html.H3("¿Quién está en riesgo hoy? Score del modelo", style={"color": TINTA, "marginBottom": "4px"}),
    html.P([
        "Probabilidad de cancelar en los 60 días siguientes al 31-oct-2026, según el modelo Extra Trees "
        "calibrado de la Evidencia 4. Usa los filtros de plan, segmento e industria; el periodo no aplica porque "
        "el score es la foto de hoy. En la prueba de agosto, el ",
        html.B("decil 1"), " (10 % de cuentas con mayor score) canceló ", html.B("2.3 veces"), " más que el promedio.",
    ], style={"color": GRIS, "fontSize": "13px", "marginTop": "0"}),
    html.Div(id="aviso-score"),
    html.Div([
        tarjeta("Cuentas evaluadas hoy", "kpi-score-cuentas", nota="Activas al 31-oct-2026"),
        tarjeta("Prioridad: decil 1", "kpi-score-decil", nota="10 % de mayor score de la cartera", alerta=True),
        tarjeta("Sobre el umbral del modelo", "kpi-score-umbral", nota=f"Score ≥ {UMBRAL_MODELO:.1%} (umbral F2)"),
        tarjeta("Decil 1 con WhatsApp Web desconectado", "kpi-score-wa", nota="Revisar primero el canal"),
    ], style=ESTILO_FILA),
    html.Div([
        html.Div(grafica("grafica-score-perfil", alto="300px"), style={"flex": "3"}),
        html.Div([
            html.Div("Qué hacer con cada perfil", style={"fontWeight": "700", "color": TINTA, "marginBottom": "8px"}),
            *[html.Div([
                html.Span(perfil, style={"backgroundColor": color, "color": "white", "fontWeight": "600",
                                         "fontSize": "12px", "padding": "3px 10px", "borderRadius": "999px"}),
                html.Div(ACCION_PERFIL[perfil], style={"fontSize": "13px", "color": TINTA, "margin": "6px 0 14px 0"}),
            ]) for perfil, color in COLOR_PERFIL.items()],
        ], style={**ESTILO_TARJETA, "flex": "2"}),
    ], style=ESTILO_FILA),
    html.Div([
        html.Label("Ver perfiles", style={**ESTILO_ETIQUETA, "marginTop": "0"}),
        dcc.Dropdown(id="filtro-perfil", options=list(COLOR_PERFIL), value=list(COLOR_PERFIL), multi=True),
        html.P(id="texto-score", style={"color": GRIS, "fontSize": "13px"}),
        tabla("tabla-score", COLUMNAS_SCORE, page_size=10, sort_action="native",
              export_format="csv", export_headers="display",
              style_data_conditional=[
                  {"if": {"filter_query": "{Decil} = 1", "column_id": "Score (%)"}, "color": ROJO, "fontWeight": "700"},
                  *[{"if": {"filter_query": f'{{Perfil}} = "{perfil}"', "column_id": "Perfil"}, "color": color,
                     "fontWeight": "600"} for perfil, color in COLOR_PERFIL.items()],
              ]),
        html.P("El botón Export descarga la lista de revisión. El score ordena a quién llamar primero; el perfil "
               "dice qué ofrecer. Es una probabilidad, no una certeza: muchas cuentas del decil 1 no cancelan.",
               style={"color": GRIS, "fontSize": "12px", "marginBottom": "0"}),
    ], style={**ESTILO_TARJETA, "marginBottom": "16px"}),

    # --- Gráfica ancha ---
    html.Div(grafica("grafica-antes-baja", alto="340px"), style={"marginBottom": "16px"}),

    # --- Detalle en pestañas ---
    html.Div(dcc.Tabs(id="pestanas", value="riesgo", children=[
        dcc.Tab(label="Cuentas con mayor caída", value="riesgo", children=[
            html.P(id="texto-tabla", style={"color": GRIS, "fontSize": "13px", "marginTop": "12px"}),
            tabla("tabla-riesgo", COLUMNAS_RIESGO, page_size=10, sort_action="native", style_data_conditional=[
                {"if": {"filter_query": '{Desenlace a 60 días} = "Canceló"'}, "color": ROJO, "fontWeight": "600"},
            ]),
        ]),
        dcc.Tab(label="¿Por qué se van?", value="motivos", children=[
            dcc.Graph(id="grafica-motivos", style={"height": "380px"}),
            html.P("La caída de uso dice cuándo actuar; el motivo de cancelación dice qué ofrecer.",
                   style={"color": GRIS, "fontSize": "13px"}),
        ]),
        dcc.Tab(label="Cómo leer el tablero", value="ayuda", children=[
            dcc.Markdown(TEXTO_AYUDA, style={"padding": "8px 4px"}),
        ]),
    ]), style=ESTILO_TARJETA),
], style=ESTILO_CONTENIDO)

app.layout = html.Div([barra_lateral, contenido], style=ESTILO_PAGINA)


# =============================================================================
# 6. Callback: un solo callback actualiza todo el tablero
#    Los argumentos llegan en el mismo orden que los Input, y el return
#    devuelve los valores en el mismo orden que los Output.
# =============================================================================
@app.callback(
    Output("texto-periodo", "children"),       # 1
    Output("kpi-activas", "children"),         # 2
    Output("kpi-activas-nota", "children"),    # 3
    Output("kpi-caida", "children"),           # 4
    Output("kpi-churn", "children"),           # 5
    Output("kpi-riesgo", "children"),          # 6
    Output("kpi-riesgo-nota", "children"),     # 7
    Output("grafica-corte", "figure"),         # 8
    Output("grafica-nivel", "figure"),         # 9
    Output("grafica-senales", "figure"),       # 10
    Output("grafica-uso-canal", "figure"),     # 11
    Output("tabla-senales", "data"),           # 12
    Output("grafica-antes-baja", "figure"),    # 13
    Output("texto-tabla", "children"),         # 14
    Output("tabla-riesgo", "data"),            # 15
    Output("grafica-motivos", "figure"),       # 16
    Output("aviso-vacio", "children"),         # 17
    Output("kpi-score-cuentas", "children"),   # 18  (Evidencia 5: score del modelo)
    Output("kpi-score-decil", "children"),     # 19
    Output("kpi-score-umbral", "children"),    # 20
    Output("kpi-score-wa", "children"),        # 21
    Output("grafica-score-perfil", "figure"),  # 22
    Output("texto-score", "children"),         # 23
    Output("tabla-score", "data"),             # 24
    Output("aviso-score", "children"),         # 25
    Input("filtro-periodo", "value"),
    Input("filtro-plan", "value"),
    Input("filtro-segmento", "value"),
    Input("filtro-industria", "value"),
    Input("filtro-perfil", "value"),
)
def actualizar(rango, planes, segmentos, industrias, perfiles):
    inicio, fin = CORTES[rango[0]], CORTES[rango[1]]
    texto_periodo = f"Periodo: {etiqueta_mes(inicio)} a {etiqueta_mes(fin)} · Datos al 31-oct-2026"
    industrias = industrias or TODAS_INDUSTRIAS  # Industria vacía = todas

    # --- Un solo bloque de filtrado ---
    filtrados = base[
        base["corte"].between(inicio, fin)
        & base["plan"].isin(planes or [])
        & base["segmento"].isin(segmentos or [])
        & base["industria"].isin(industrias)
    ]

    # --- Score de hoy: mismos filtros de plan, segmento e industria (el periodo no aplica) ---
    if SCORES is None:
        hoy = pd.DataFrame(columns=["account_id", "decil_riesgo", "score", "estado_wa", "perfil"])
        aviso_score = html.Div("Falta datos/scores_modelo_hoy.csv: ejecuta el notebook de la Evidencia 5 "
                               "para generarlo.", style=ESTILO_AVISO)
    else:
        hoy = SCORES[SCORES["plan"].isin(planes or []) & SCORES["segmento"].isin(segmentos or [])
                     & SCORES["industria"].isin(industrias)]
        aviso_score = None
    if hoy.empty:
        salida_score = ("—", "—", "—", "—", figura_vacia("Sin cuentas con score para estos filtros"), "", [], aviso_score)
    else:
        lista = tabla_score(hoy, perfiles or [])
        salida_score = (
            *indicadores_score(hoy),                                         # 18-21
            figura_score_perfil(hoy),                                        # 22
            f"{len(lista):,} cuentas, de mayor a menor score. Empates: primero la mayor caída de chats.",  # 23
            registros(lista),                                                # 24
            aviso_score,                                                     # 25
        )

    # --- Selección vacía: misma cantidad de valores que el return normal ---
    if filtrados.empty:
        vacia = figura_vacia("Sin datos para los filtros seleccionados")
        aviso = html.Div("No hay cuentas con esos filtros. Amplía la selección.", style=ESTILO_AVISO)
        return (
            texto_periodo,                 # 1
            "—", "",                        # 2, 3
            "—",                            # 4
            "—",                            # 5
            "—", "",                        # 6, 7
            vacia, vacia, vacia, vacia,     # 8, 9, 10, 11
            [],                             # 12
            vacia,                          # 13
            "",                             # 14
            [],                             # 15
            vacia,                          # 16
            aviso,                          # 17
            *salida_score,                  # 18-25
        )

    # --- Cálculos con los datos filtrados ---
    kpis = indicadores(filtrados)
    con_desenlace = filtrados[filtrados["churn_60d"].notna()]

    senales = comparar_senales(filtrados)
    fig_senales = figura_senales(senales) if not senales.empty else figura_vacia("Churn a 60 días con y sin cada señal")
    fig_uso_canal = figura_uso_canal(filtrados)
    if fig_uso_canal is None:
        fig_uso_canal = figura_vacia("¿El canal suma algo al uso?")

    bajas = antes_baja[
        antes_baja["plan"].isin(planes or [])
        & antes_baja["segmento"].isin(segmentos or [])
        & antes_baja["industria"].isin(industrias)
        & (antes_baja["fecha_baja"] > inicio)
        & (antes_baja["fecha_baja"] <= fin + pd.Timedelta(days=HORIZONTE_DIAS))
    ]
    referencia = con_desenlace.loc[con_desenlace["churn_60d"] == 0, "prop_dias_activos"].median() * 100

    riesgo = tabla_en_riesgo(filtrados)
    ultimo = filtrados["corte"].max()
    texto_tabla = (f"{len(riesgo):,} cuentas tienen caída ≥50% de chats al cierre de {etiqueta_mes(ultimo)}. "
                   "Son las primeras que Customer Success debería revisar.")

    # Aviso informativo si el periodo elegido todavía no tiene desenlace (sep y oct)
    aviso = None
    if con_desenlace.empty:
        aviso = html.Div("Septiembre y octubre todavía no tienen desenlace a 60 días. "
                         "Incluye algún mes entre mayo y agosto para ver el churn.", style=ESTILO_AVISO)

    return (
        texto_periodo,                                   # 1
        kpis["activas"], kpis["activas_nota"],           # 2, 3
        kpis["caida"],                                   # 4
        kpis["churn"],                                   # 5
        kpis["veces"], kpis["veces_nota"],               # 6, 7
        figura_por_corte(filtrados),                     # 8
        figura_por_nivel(filtrados),                     # 9
        fig_senales,                                     # 10
        fig_uso_canal,                                   # 11
        registros(senales),                              # 12
        figura_antes_baja(bajas, referencia),            # 13
        texto_tabla,                                     # 14
        registros(riesgo),                               # 15
        figura_motivos(filtrados),                       # 16
        aviso,                                           # 17
        *salida_score,                                   # 18-25
    )


if __name__ == "__main__":
    app.run(debug=True, port=8050)
