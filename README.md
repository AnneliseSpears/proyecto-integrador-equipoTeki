# Proyecto integrador - Equipo Teki

Nombre del proyecto: LeadSales · Monitor de adopción y riesgo de churn

> **Pregunta directiva:** ¿Cómo identificar si la baja adopción de funcionalidades y canales anticipa la cancelación?

## Estructura
- docs/ux: entregables de UX
- docs/ui: entregables de UI
- app: código de la plataforma (Streamlit)
- datos: archivos que usa el tablero

## Cambio de enfoque del tablero (a partir del Laboratorio 9)

En los primeros laboratorios de Streamlit el tablero solo mostraba las **cancelaciones** y sus motivos. Con la **Evidencia 4** (modelado) ya contamos con los datos v3 de LeadSales (corte 31-oct-2026) y con una respuesta a nuestra pregunta. Por eso reenfocamos el tablero para que la conteste directamente:

- **Antes:** ¿cuántas cuentas cancelan y por qué?
- **Ahora:** ¿las cuentas que bajan su uso cancelan más en los 60 días siguientes? ¿Cuáles debería revisar primero Customer Success?

Las cancelaciones no se eliminan: ahora son la pestaña **"¿Por qué se van?"**. La caída de uso dice *cuándo* actuar y el motivo de cancelación dice *qué* ofrecer.

Este enfoque es también más fiel al wireframe del Dashboard principal en Figma, que ya estaba diseñado alrededor de la adopción y de la tabla "Cuentas con mayor disminución de actividad".

## Datos

| Archivo | Qué contiene |
|---|---|
| `datos/panel_mensual.csv` | Una fila por cuenta y mes: chats, días activos, plan, segmento, industria |
| `datos/perfil_cuentas.csv` | Una fila por cuenta: fecha de alta y de baja (el desenlace) |
| `datos/cancelaciones.csv` | Motivo que dio cada cuenta al cancelar |

## Cómo correrlo

```
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
streamlit run app/app.py
```

### Render
https://prueba-render-mwxj.onrender.com/
