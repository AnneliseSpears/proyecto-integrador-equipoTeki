from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
 
st.set_page_config(page_title="Tablero de ventas", layout="wide")
 
RUTA = Path("proyecto-integrador-equipoTeki") / "datos" / "cancelaciones_limpias.parquet"

datos = pd.read_parquet(RUTA)
datos["fecha"] = pd.to_datetime(datos["fecha"])
 
st.write(datos.shape)
st.write(datos.columns.tolist())
st.dataframe(datos.head(20))


# --- Configuración de la página ---
st.set_page_config(
    page_title="Customer Success | Riesgo de Churn",
    layout="wide"
)

# --- Datos inventados ---
datos = pd.DataFrame({
    "Cuenta": [
        "Cuenta Alfa", "Cuenta Beta", "Cuenta Gamma",
        "Cuenta Delta", "Cuenta Epsilon", "Cuenta Zeta",
        "Cuenta Eta", "Cuenta Theta"
    ],
    "Segmento": [
        "Enterprise", "PyME", "Enterprise", "PyME",
        "Enterprise", "PyME", "Enterprise", "PyME"
    ],
    "Riesgo": [
        "Alto", "Medio", "Alto", "Bajo",
        "Medio", "Alto", "Bajo", "Medio"
    ],
    "Probabilidad de churn": [89, 65, 82, 18, 57, 91, 12, 48],
    "Días sin actividad": [45, 20, 38, 5, 25, 52, 3, 18],
    "Ingreso mensual": [
        25000, 8000, 32000, 6000,
        28000, 12000, 35000, 9000
    ],
    "KAM": [
        "Ana", "Carlos", "Ana", "Luis",
        "Carlos", "Luis", "Ana", "Carlos"
    ],
    "Estado": [
        "En seguimiento", "Pendiente", "En seguimiento",
        "Estable", "Pendiente", "En seguimiento",
        "Estable", "Pendiente"
    ]
})

# --- Barra lateral ---
with st.sidebar:
    st.title("Customer Success")
    st.caption("Panel de gestión de clientes")

    st.divider()

    st.subheader("Navegación")
    seccion = st.radio(
        "Seleccionar sección",
        ["Dashboard", "Cuentas", "Seguimiento"]
    )

    st.divider()

    st.subheader("Filtros")

    segmento = st.selectbox(
        "Segmento",
        ["Todos"] + list(datos["Segmento"].unique())
    )

    riesgo = st.selectbox(
        "Nivel de riesgo",
        ["Todos", "Alto", "Medio", "Bajo"]
    )

    kam = st.selectbox(
        "Key Account Manager",
        ["Todos"] + list(datos["KAM"].unique())
    )

# --- Aplicar filtros ---
filtrados = datos.copy()

if segmento != "Todos":
    filtrados = filtrados[filtrados["Segmento"] == segmento]

if riesgo != "Todos":
    filtrados = filtrados[filtrados["Riesgo"] == riesgo]

if kam != "Todos":
    filtrados = filtrados[filtrados["KAM"] == kam]

# --- Encabezado principal ---
st.title("Dashboard de Riesgo de Churn")
st.caption("Monitoreo de cuentas y seguimiento de Customer Success")

st.divider()

# --- Indicadores principales ---
total_cuentas = len(filtrados)

cuentas_alto = len(
    filtrados[filtrados["Riesgo"] == "Alto"]
)

probabilidad_promedio = (
    filtrados["Probabilidad de churn"].mean()
    if total_cuentas > 0 else 0
)

c1, c2, c3 = st.columns(3)

c1.metric(
    "Cuentas analizadas",
    total_cuentas
)

c2.metric(
    "Cuentas en riesgo alto",
    cuentas_alto
)

c3.metric(
    "Probabilidad promedio de churn",
    f"{probabilidad_promedio:.1f}%"
)

st.divider()

# --- Gráfica de distribución de riesgo ---
st.subheader("Distribución de cuentas por nivel de riesgo")

orden = ["Alto", "Medio", "Bajo"]

conteo_riesgo = (
    filtrados["Riesgo"]
    .value_counts()
    .reindex(orden, fill_value=0)
    .reset_index()
)

conteo_riesgo.columns = ["Nivel de riesgo", "Cuentas"]

figura = px.bar(
    conteo_riesgo,
    x="Nivel de riesgo",
    y="Cuentas",
    text="Cuentas",
    title="Cuentas según nivel de riesgo"
)

figura.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    showlegend=False
)

st.plotly_chart(figura, use_container_width=True)

st.divider()

# --- Tabla principal ---
st.subheader("Cuentas de clientes")

st.caption("Listado de cuentas según los filtros seleccionados.")

st.dataframe(
    filtrados,
    use_container_width=True,
    hide_index=True
)

st.divider()

# --- Secciones de detalle ---
tab1, tab2, tab3 = st.tabs([
    "Detalle de cuenta",
    "Seguimiento KAM",
    "Datos"
])

with tab1:
    st.subheader("Información de una cuenta")

    if not filtrados.empty:
        cuenta_seleccionada = st.selectbox(
            "Seleccionar cuenta",
            filtrados["Cuenta"].tolist()
        )

        detalle = filtrados[
            filtrados["Cuenta"] == cuenta_seleccionada
        ].iloc[0]

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Cuenta:**", detalle["Cuenta"])
            st.write("**Segmento:**", detalle["Segmento"])
            st.write("**Nivel de riesgo:**", detalle["Riesgo"])
            st.write(
                "**Probabilidad de churn:**",
                f'{detalle["Probabilidad de churn"]}%'
            )

        with col2:
            st.write(
                "**Días sin actividad:**",
                detalle["Días sin actividad"]
            )
            st.write(
                "**Ingreso mensual:**",
                f'${detalle["Ingreso mensual"]:,}'
            )
            st.write("**KAM:**", detalle["KAM"])
            st.write("**Estado:**", detalle["Estado"])
    else:
        st.info("No hay cuentas disponibles con los filtros seleccionados.")

with tab2:
    st.subheader("Seguimiento de Key Account Managers")

    st.dataframe(
        filtrados[[
            "Cuenta", "KAM", "Riesgo", "Estado"
        ]],
        use_container_width=True,
        hide_index=True
    )

with tab3:
    st.subheader("Datos utilizados")

    st.write(
        "Esta tabla contiene datos de ejemplo creados "
        "manualmente para representar las cuentas del proyecto."
    )

    st.dataframe(
        filtrados,
        use_container_width=True,
        hide_index=True
    )

# --- Pie de página ---
st.divider()

st.caption(
    "Proyecto de análisis de Customer Churn | "
    "Datos simulados para demostración"
)
