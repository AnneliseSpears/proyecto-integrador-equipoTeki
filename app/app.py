from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
#import time

# 1. Configuración de la página
st.set_page_config(page_title="Tablero de cancelaciones", layout="wide")

# Función para cargar datos
@st.cache_data
def cargar(ruta):

    #time.sleep(2)  # Simula una consulta lenta

    return pd.read_parquet(ruta)

# Cargar datos
RUTA = Path(__file__).parent.parent / "datos" / "cancelaciones_limpias.parquet"

datos = cargar(RUTA)

datos["fecha"] = pd.to_datetime(datos["fecha"])
datos["dia"] = datos["fecha"].dt.date

#st.write(datos.shape)
#st.write(datos.columns.tolist())
#st.dataframe(datos.head(20))

# --- Configuración de la página ---
st.set_page_config(
    page_title="Customer Success | Riesgo de Churn",
    layout="wide"
)

# 3. Filtros laterales
with st.sidebar:

    st.header("Filtros")

    grupos_plan = st.multiselect(
        "Grupo de plan",
        options=sorted(datos["grupo_plan"].dropna().unique()),
        default=sorted(datos["grupo_plan"].dropna().unique()),
    )

    motivos = st.multiselect(
        "Motivo de cancelación",
        options=sorted(datos["motivo_normalizado"].dropna().unique()),
        default=sorted(datos["motivo_normalizado"].dropna().unique()),
    )

    inicio, fin = st.date_input(
        "Periodo",
        value=(datos["fecha"].min().date(), datos["fecha"].max().date()),
        min_value=datos["fecha"].min().date(),
        max_value=datos["fecha"].max().date(),
    )

# 4. Diccionario para renombrar motivos
nombres_motivos = {
    "H2_technical_issues": "Technical Issues",
    "H4_lack_of_results": "Lack of Results",
    "H5_high_pricing": "High Pricing",
    "H6_plan_fit": "Plan Fit",
    "H8_business_pause": "Business Pause",
}

# 5. Aplicar filtros
filtrados = datos[
    datos["grupo_plan"].isin(grupos_plan)
    & datos["motivo_normalizado"].isin(motivos)
    & datos["fecha"].between(
        pd.to_datetime(inicio),
        pd.to_datetime(fin)
    )
]

if filtrados.empty:
    st.warning("No hay datos con esos filtros. Amplia la seleccion.")
    st.stop()

# Descargar datos filtrados como CSV

csv = filtrados.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Descargar datos filtrados (CSV)",
    data=csv,
    file_name="cancelaciones_filtradas.csv",
    mime="text/csv",
)

# 6. Calcular métricas
cancelaciones = len(filtrados)

cuentas = filtrados["account_id"].nunique()

motivo_principal = (
    nombres_motivos.get(
        filtrados["motivo_normalizado"].mode()[0],
        filtrados["motivo_normalizado"].mode()[0]
    )
    if not filtrados.empty
    else "Sin datos"
)

dias = filtrados["fecha"].nunique()

# 7. Mostrar métricas
st.title("Tablero de cancelaciones")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Cancelaciones", f"{cancelaciones:,}")

c2.metric("Cuentas afectadas", f"{cuentas:,}")

c3.metric("Motivo principal", motivo_principal)

c4.metric("Días con registros", f"{dias}")

# Pestañas del dashboard

tab1, tab2 = st.tabs([
    "Cancelaciones por día",
    "Tabla cruzada"
])

with tab1:

    st.subheader("Análisis de cancelaciones")

    # Aquí van tus gráficas actuales


with tab2:

    st.subheader("Cancelaciones por grupo de plan y motivo")

    tabla_cruzada = filtrados.pivot_table(
        index="grupo_plan",
        columns="motivo_normalizado",
        values="account_id",
        aggfunc="count",
        fill_value=0
    )

    # Renombrar columnas para facilitar la lectura
    tabla_cruzada = tabla_cruzada.rename(
        columns=nombres_motivos
    )

    st.dataframe(
        tabla_cruzada,
        use_container_width=True
    )

# Cancelaciones por día
por_dia = filtrados.groupby("dia", as_index=False).size()
por_dia = por_dia.rename(columns={"size": "cancelaciones"})

st.plotly_chart(
    px.line(
        por_dia,
        x="dia",
        y="cancelaciones",
        title="Cancelaciones por día",
        labels={
            "dia": "Fecha",
            "cancelaciones": "Número de cancelaciones"
        }
    ),
    use_container_width=True
)

# 2. Gráficas por motivo y grupo de plan
izq, der = st.columns(2)

# Cancelaciones por motivo
por_cat = (
    filtrados.groupby("motivo_normalizado")
    .size()
    .reset_index(name="cancelaciones")
)

por_cat["motivo"] = por_cat["motivo_normalizado"].map(
    nombres_motivos
).fillna(por_cat["motivo_normalizado"])

izq.plotly_chart(
    px.bar(
        por_cat,
        x="motivo",
        y="cancelaciones",
        title="Cancelaciones por motivo",
        labels={
            "motivo": "Motivo de cancelación",
            "cancelaciones": "Número de cancelaciones"
        }
    ),
    use_container_width=True
)

# Cancelaciones por grupo de plan
por_suc = (
    filtrados.groupby("grupo_plan")
    .size()
    .reset_index(name="cancelaciones")
)

der.plotly_chart(
    px.bar(
        por_suc,
        x="grupo_plan",
        y="cancelaciones",
        title="Cancelaciones por grupo de plan",
        labels={
            "grupo_plan": "Grupo de plan",
            "cancelaciones": "Número de cancelaciones"
        }
    ),
    use_container_width=True
)
