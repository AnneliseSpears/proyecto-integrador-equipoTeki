# Proyecto integrador - Equipo Teki

Nombre del proyecto: LeadSales · Monitor de adopción y riesgo de churn

> **Pregunta directiva:** ¿Cómo identificar si la baja adopción de funcionalidades y canales anticipa la cancelación?

## Estructura
- docs/ux: entregables de UX
- docs/ui: entregables de UI
- app: tablero en Streamlit (`streamlit run app/app.py`)
- dash: el mismo tablero en Dash (`python dash/app.py`)
- datos: archivos que usa el tablero

## Cambio de enfoque del tablero (a partir del Laboratorio 9)

En los primeros laboratorios de Streamlit el tablero solo mostraba las **cancelaciones** y sus motivos. Con la **Evidencia 4** (modelado) ya contamos con los datos v3 de LeadSales (corte 31-oct-2026) y con una respuesta a nuestra pregunta. Por eso reenfocamos el tablero para que la conteste directamente:

- **Antes:** ¿cuántas cuentas cancelan y por qué?
- **Ahora:** ¿las cuentas que bajan su uso o desconectan su canal cancelan más en los 60 días siguientes? ¿Qué señal anticipa mejor la cancelación? ¿Cuáles cuentas debería revisar primero Customer Success?

Las cancelaciones no se eliminan: ahora son la pestaña **"¿Por qué se van?"**. La caída de uso dice *cuándo* actuar y el motivo de cancelación dice *qué* ofrecer.

Este enfoque es también más fiel al wireframe del Dashboard principal en Figma, que ya estaba diseñado alrededor de la adopción y de la tabla "Cuentas con mayor disminución de actividad".

## Datos

| Archivo | Qué contiene |
|---|---|
| `datos/panel_mensual.csv` | Una fila por cuenta y mes: chats, días activos, plan, segmento, industria |
| `datos/perfil_cuentas.csv` | Una fila por cuenta: fecha de alta y de baja (el desenlace) |
| `datos/cancelaciones.csv` | Motivo que dio cada cuenta al cancelar |
| `datos/historial_canales_eventos.csv` | Conexiones y desconexiones de canales (se usa WhatsApp Web) |

## Qué responde el tablero

| Parte de la pregunta | Cómo se mide | Dónde se ve |
|---|---|---|
| Baja adopción de **funcionalidades** (uso) | Caída ≥50% de chats, días activos y uso bajo 2 meses seguidos | Indicadores, gráficas principales y comparación de señales |
| Baja adopción de **canales** | WhatsApp Web desconectado al cierre del mes | Comparación de señales y gráfica "¿El canal suma algo al uso?" |
| **Anticipa** la cancelación | Cuentas activas al cierre de cada mes que cancelan en los 60 días siguientes | Todo el tablero |
| ¿A quién revisar primero? | Cuentas con la señal en el último mes | Tabla "Cuentas con mayor caída" |
| ¿Por qué se van? | Motivo de la encuesta de cancelación | Pestaña "¿Por qué se van?" |

## Cómo correrlo

```
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
streamlit run app/app.py      # versión Streamlit
python dash/app.py            # versión Dash (http://localhost:8050)
```

### Render
https://prueba-render-mwxj.onrender.com/
