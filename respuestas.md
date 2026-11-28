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

- Medimos la adopción de **funcionalidades** con el uso: **caída de 50% o más en los chats** contra los dos meses anteriores, **proporción de días activos** y **uso bajo dos meses seguidos**.
- Medimos la adopción de **canales** con el estado de **WhatsApp Web** al cierre del mes, con las reglas de la Evidencia 4 (las desconexiones de menos de 24 h no cuentan).
- Un bloque compara todas las señales lado a lado (uso, canal, mora y soporte) para responder qué tipo de baja adopción anticipa la cancelación.
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

## Datos que usamos

En lugar del `ventas.csv` de ejemplo usamos los datos propios del proyecto (versión 3 de LeadSales, corte 31-oct-2026), guardados en `datos/`:

- `panel_mensual.csv`: uso por cuenta y mes (chats, días activos, plan, segmento, industria).
- `perfil_cuentas.csv`: fecha de alta y de baja de cada cuenta.
- `cancelaciones.csv`: motivo que dio cada cuenta al cancelar.

Los tres se leen con una ruta construida con `Path(__file__)` y con `parse_dates` en sus columnas de fecha. Los filtros (periodo, plan, segmento e industria) sacan sus opciones de los datos, y todo el tablero se calcula a partir de un solo bloque de filtrado.

## Parte C · Medición del caché

Simulamos una fuente lenta con `time.sleep(2)` dentro de la función que carga los datos. Medimos con cronómetro, moviendo los filtros de plan, segmento e industria.

| | Primera carga | Al mover el filtro |
|---|---|---|
| Sin `@st.cache_data` | 5 s | 5 s |
| Con `@st.cache_data` | 3 s | 4.6 s en promedio (6, 7, 4, 2 y 4 s en 5 intentos) |

**Conclusión:** sin caché, cada vez que movemos un filtro Streamlit vuelve a correr el script completo y vuelve a leer los tres archivos, con todo y la espera de la consulta lenta. Con `@st.cache_data`, la primera carga sigue tardando porque es la que llena el caché, pero después los datos ya no se vuelven a leer y lo que queda es solo recalcular y dibujar el tablero.

**Nota sobre nuestra medición:** al mover los filtros, la diferencia que medimos fue menor que los 2 segundos de la espera simulada. Lo atribuimos a dos cosas: medimos a mano con cronómetro, lo que tiene un margen de error de 1 a 2 segundos, y nuestro tablero tarda varios segundos en dibujar sus gráficas y tablas en la laptop, con o sin caché. Aun así, dejamos el `@st.cache_data`, porque en Render, con datos reales y varias personas conectadas, leer los archivos en cada interacción sí haría lenta la aplicación.

Al terminar la medición quitamos el `time.sleep(2)` y el `import time`, y dejamos el `@st.cache_data`.

---

# Laboratorio 11 · Dash, el layout como árbol de componentes

Construimos el mismo tablero de Streamlit en `dash/app.py`, con los mismos datos y los mismos cálculos, incluida la comparación de señales de uso, canal y contexto (los indicadores dan exactamente lo mismo: 2,059 cuentas activas, 11.9% con caída, 10.6% de churn y 3.3× más riesgo con caída). Los filtros ya tienen su `id`, pero todavía no hacen nada: se conectan con callbacks en el Laboratorio 12.

## Bitácora de comparación

| Pregunta | Nuestra respuesta |
|---|---|
| ¿Qué les resultó más fácil en Dash que en Streamlit? | Acomodar los bloques donde los queríamos. Con `display: flex` y los diccionarios de estilo controlamos el ancho de cada tarjeta, la barra lateral y la separación entre bloques. También fue práctico escribir funciones como `tarjeta()` o `grafica()` que devuelven un pedazo del árbol y reutilizarlas. |
| ¿Qué les resultó más difícil o más lento? | Escribir el layout: hay que cuidar los corchetes y paréntesis del árbol, y cada estilo se define a mano en camelCase. En Streamlit con una línea (`st.metric`, `st.columns`) ya teníamos el resultado. Además, en Dash los filtros no hacen nada hasta escribir los callbacks, mientras que en Streamlit funcionan desde el inicio. |
| ¿Hay algo de su wireframe original que en Streamlit no pudieron construir y en Dash sí? | Sí. La barra lateral con el menú de pantallas (Dashboard, Explorador, Perfil 360, Análisis) y el ancho fijo de 240 px; la tarjeta de riesgo marcada en rojo con ícono de alerta y del doble de ancho; y la tabla con encabezado oscuro como en Figma. La columna "Ver perfil" clicable todavía no, porque necesita callbacks. |
| Con lo visto hasta hoy, ¿con cuál se inclinan? ¿Por qué? | Por ahora nos inclinamos por Dash, porque se parece más a nuestro wireframe y nos deja agregar las pantallas del Explorador y el Perfil 360. Pero Streamlit fue mucho más rápido de construir. La decisión final depende de qué tan complicados sean los callbacks en el Laboratorio 12. |
