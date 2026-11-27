# Respuestas · Equipo Teki

# Laboratorio 9 · Streamlit, primeros pasos

## B.1 Predicción (escrita antes de ejecutar)

En primer lugar, aparecerá un separador en el sitio web. A continuación, se crea un contador que comienza en 0, junto con un botón que incrementa el valor en 1 cada vez que se pulsa. Por último, la pantalla mostrará el valor del contador.

**Lo que pasó realmente:** el contador nunca pasó de 1, sin importar cuántas veces presionamos el botón. Nuestra predicción suponía que el valor se iba acumulando (llegaría a 5), y no fue así.

## B.3 Preguntas

**1. ¿Por qué el contador nunca pasa de 1, por más veces que presionen el botón?**

Annelise: Porque Streamlit vuelve a ejecutar todo el código cada vez que presionamos el botón. Como el contador empieza nuevamente en 0, solamente puede llegar a 1 en cada ejecución.

Arlet: Porque cada vez que hacemos clic, el programa vuelve a empezar desde la primera línea y reinicia el contador en 0. Después suma uno, pero no recuerda el resultado anterior.

Miguel: Esto sucede porque Streamlit ejecuta nuevamente todo el script después de cada interacción. La variable contador se inicializa en 0 cada vez, por lo que al presionar el botón solamente aumenta a 1.

Francesco: Porque el contador se reinicia a 0 cada vez que presionamos el botón. Por eso, siempre vuelve a sumar solamente uno.

**2. Si quisieran que el valor se conservara entre una interacción y la siguiente, ¿dónde tendría que guardarse, si no puede ser en una variable normal del script?**

Annelise: Tendría que guardarse en un espacio que conserve la información entre ejecuciones, como st.session_state, en lugar de una variable normal.

Arlet: Se tendría que guardar en una variable especial de Streamlit llamada st.session_state, que permite mantener los valores aunque el programa se vuelva a ejecutar.

Miguel: El valor debería almacenarse en st.session_state, ya que funciona como un espacio de almacenamiento que mantiene los datos durante las diferentes interacciones del usuario.

Francesco: En st.session_state, porque permite guardar información sin que se reinicie cada vez que Streamlit ejecuta el código.

## Cambio de enfoque del tablero

Con la Evidencia 4 obtuvimos los datos v3 de LeadSales (panel mensual de uso, perfil de cuentas y cancelaciones, corte 31-oct-2026). Por eso, desde este laboratorio, el tablero deja de mostrar solo las cancelaciones y se enfoca en nuestra pregunta directiva: **¿cómo identificar si la baja adopción de funcionalidades y canales anticipa la cancelación?**

- La señal principal es la **caída de 50% o más en los chats** del mes contra los dos meses anteriores, junto con la **proporción de días activos**.
- Para cada cuenta activa al cierre de un mes revisamos si canceló en los **60 días siguientes**.
- Las cancelaciones se quedan como la pestaña "¿Por qué se van?": la caída de uso dice cuándo actuar y el motivo dice qué ofrecer.

## Parte C · Verificación contra el wireframe

Comparamos el tablero con el wireframe *Dashboard principal* de Figma (página "4. Wireframes 2").

| Pregunta | Sí / No |
|---|---|
| ¿Los bloques están en el mismo orden vertical que en el wireframe? | Sí: título y periodo → 4 indicadores → dos gráficas lado a lado → tabla "Cuentas con mayor caída" |
| ¿Los filtros están en el mismo lugar que los diseñaron? | Sí: barra lateral izquierda con periodo, plan, segmento e industria (los mismos del wireframe, salvo "Estado", porque el tablero solo analiza cuentas activas al corte) |
| ¿La cantidad de indicadores coincide con el diseño? | Sí: 4 indicadores (cuentas activas, % con caída de actividad, churn a 60 días y riesgo con caída) |
| ¿Hay algo en el wireframe que no supieron construir con st.columns, st.tabs o st.expander? | Sí (ver abajo) |

**Elementos del wireframe que no pudimos construir tal cual en Streamlit:**

- **Navegación entre pantallas en la barra lateral** (Dashboard, Explorador, Perfil 360, Análisis). Con `st.columns`, `st.tabs` o `st.expander` no se arma un menú de páginas. Requiere una app de varias páginas.
- **Columna "Ver perfil" clicable en la tabla.** `st.dataframe` muestra datos, pero no permite que una fila lleve a otra pantalla.
- **Tarjetas de indicador con ícono de alerta y color propio.** `st.metric` solo permite el número y la variación con su color automático. No se puede poner un ícono ni elegir el color.
- **Ancho fijo de la barra lateral (240 px) y posición exacta de los bloques.** Streamlit decide el ancho y el espaciado.
- **Gráfica de adopción por canal.** La quitamos a propósito: en la Evidencia 4 la conexión de canales no anticipó la baja y sus datos tienen problemas de calidad. En su lugar mostramos el churn según los días activos.

Esto lo tomaremos en cuenta en la sesión de Dash, que permite colocar elementos con más libertad.

---

# Laboratorio 10 · Datos, filtros y caché

## Medir el caché

Sin @st.cache_data: 1er carga --> ~3 segundos, Al mover el filtro --> 2 segundos

Con @st.cache_data: 1er carga --> 1 segundo, Al mover el filtro --> casi inmediata
