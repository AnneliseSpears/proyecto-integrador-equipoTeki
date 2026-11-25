# Estructura de la Plataforma

## Archivo de Figma

* **Nombre del archivo:** `Equipo Teky - LeadSales: Monitor de adopción y abandono`

* **Enlace de Figma:** https://www.figma.com/design/hqG6A2stQoI7cYATZNNL0J/Laboratorio-6?node-id=0-1&t=FpzCHxzOcR3iqE9b-1

## Pantallas

1. **Dashboard Principal**

   * **Descripción:** Pantalla inicial de la plataforma donde el equipo de Customer Success puede consultar una visión general de la adopción y actividad de las cuentas. Incluye indicadores principales, tendencias mensuales de uso y una lista de cuentas que presentan disminuciones importantes en su actividad. También permite aplicar filtros por período, segmento, plan y estado de la cuenta.

   * **Objetivo de UX:** Facilitar la identificación rápida de patrones de baja adopción y posibles señales tempranas de churn, sin tener que revisar cada cuenta individualmente.

2. **Explorador de Cuentas**

   * **Descripción:** Pantalla que permite buscar, filtrar y comparar cuentas mediante una tabla con información como Account ID, nombre, estado, antigüedad, número de chats, mensajes, leads, días activos y variación de actividad. Desde esta pantalla, el usuario puede seleccionar una cuenta para consultar su información detallada.

   * **Objetivo de UX:** Simplificar la búsqueda y priorización de cuentas que requieren una revisión más profunda por parte del equipo de Customer Success.

3. **Perfil 360 de la Cuenta**

   * **Descripción:** Pantalla que reúne la información disponible de una cuenta en un solo lugar. Incluye datos generales, plan, segmento, antigüedad, estado, indicadores de adopción de funcionalidades y canales, así como el historial mensual de actividad. También permite consultar información adicional de soporte cuando se encuentra disponible.

   * **Objetivo de UX:** Proporcionar una visión integral del comportamiento de cada cuenta para facilitar la investigación de posibles problemas de adopción y continuidad de uso.

4. **Análisis de Adopción y Señales de Churn**

   * **Descripción:** Pantalla enfocada en analizar la relación entre la adopción de funcionalidades, la actividad de las cuentas y la cancelación. Incluye gráficos comparativos, tendencias de uso e indicadores de disminución de actividad. Permite identificar patrones que podrían funcionar como señales de alerta y revisar las cuentas que presentan deterioro persistente en su actividad.

   * **Objetivo de UX:** Ayudar al equipo a comprender qué comportamientos podrían anticipar una cancelación y respaldar decisiones de seguimiento mediante información analítica.

## Trazabilidad con UX

1. **Identificación rápida de cuentas con baja adopción**

   * **Requerimiento atendido:** Permitir que el equipo de Customer Success identifique cuentas con niveles bajos o decrecientes de actividad.

   * **Pantallas involucradas:** Dashboard Principal y Explorador de Cuentas.

   * **Justificación / Solución UX:** Se presentan indicadores generales y tendencias de actividad en el Dashboard, mientras que el Explorador permite filtrar y ordenar las cuentas para identificar aquellas que requieren atención.

2. **Centralización de la información de cada cuenta**

   * **Requerimiento atendido:** Facilitar la consulta de información de una cuenta sin tener que revisar múltiples fuentes de datos por separado.

   * **Pantallas involucradas:** Explorador de Cuentas y Perfil 360 de la Cuenta.

   * **Justificación / Solución UX:** Se propone una vista consolidada que reúne información del perfil, adopción, actividad mensual e historial disponible, facilitando la investigación del comportamiento de cada cuenta.

3. **Análisis de señales relacionadas con churn**

   * **Requerimiento atendido:** Identificar patrones de baja adopción y disminución de actividad que podrían estar relacionados con una futura cancelación.

   * **Pantallas involucradas:** Dashboard Principal, Perfil 360 de la Cuenta y Análisis de Adopción y Señales de Churn.

   * **Justificación / Solución UX:** Se incorporan gráficos comparativos e indicadores de actividad para facilitar la interpretación de posibles señales de riesgo. Estas señales se presentan como asociaciones que requieren validación, no como evidencia de causalidad ni como probabilidades de churn ya calculadas.

## Origen de los Datos

| No. | Pantalla / Bloque | Datos necesarios | Origen del dato / Fuente |
| ----- | ----- | ----- | ----- |
| **1** | **Dashboard Principal** | Identificador, nombre, segmento, plan y estado de las cuentas | Perfil de cuentas (`perfil_cuentas.csv`) |
| **2** | **Dashboard Principal** | Número mensual de chats, mensajes, leads y días activos | Panel mensual (`panel_mensual.csv`) |
| **3** | **Dashboard Principal** | Cuentas canceladas y fechas de cancelación | Archivo de cancelaciones (`cancelaciones.csv`) |
| **4** | **Explorador de Cuentas** | Account ID, nombre, segmento, plan, antigüedad y estado | Perfil de cuentas (`perfil_cuentas.csv`) |
| **5** | **Explorador de Cuentas** | Actividad mensual y variación de chats, mensajes y leads | Panel mensual (`panel_mensual.csv`) |
| **6** | **Perfil 360 de la Cuenta** | Información general y características de la cuenta | Perfil de cuentas (`perfil_cuentas.csv`) |
| **7** | **Perfil 360 de la Cuenta** | Indicadores de uso y conexión de canales o funcionalidades | Perfil de cuentas (`perfil_cuentas.csv`), sujeto a disponibilidad de los campos |
| **8** | **Perfil 360 de la Cuenta** | Historial de chats, mensajes, leads y días activos | Panel mensual (`panel_mensual.csv`) |
| **9** | **Perfil 360 de la Cuenta** | Información de conversaciones y soporte disponible | Conversaciones y soporte (`reuniones_samu.json` y `soporte_intercom.json`), según los datos disponibles |
| **10** | **Análisis de Adopción y Señales de Churn** | Indicadores de caída de actividad y uso reducido durante períodos consecutivos | Panel mensual (`panel_mensual.csv`) |
| **11** | **Análisis de Adopción y Señales de Churn** | Estado de cancelación y fechas asociadas | Archivo de cancelaciones (`cancelaciones.csv`) |
| **12** | **Análisis de Adopción y Señales de Churn** | Indicadores de adopción y conexión de canales | Perfil de cuentas (`perfil_cuentas.csv`) |

## User Flow y Sitemap

### Coherencia de Flujo y Estructura

* **Objetivo del Usuario:** "Quiero identificar qué cuentas presentan señales de baja adopción para investigar si podrían estar en riesgo de cancelación y decidir cuáles necesitan seguimiento por parte de Customer Success."

* **Punto de Dolor Identificado:** La información sobre adopción, actividad y comportamiento de las cuentas se encuentra distribuida entre diferentes fuentes de datos. Esto dificulta identificar rápidamente qué clientes presentan disminuciones de uso y cuáles requieren una investigación más profunda.

* **Construibilidad (Streamlit/Dash):** La plataforma se plantea como una interfaz interna de escritorio, organizada mediante una barra lateral de navegación y filtros, con indicadores, gráficos y tablas en el área principal. Las pantallas se estructuran mediante filas y columnas para facilitar su implementación en Streamlit o Dash.

### Leyenda de Accesos del Sitemap

* **Verde (Inicio / Dashboard):** Pantalla principal desde la que se accede a los indicadores generales y a las demás secciones de la plataforma.

* **Amarillo (Exploración):** Módulo para buscar, filtrar y comparar cuentas.

* **Azul (Información detallada):** Perfil 360 que reúne los datos e historial de una cuenta específica.

* **Morado (Análisis):** Módulo para estudiar tendencias de adopción y posibles señales relacionadas con churn.

## Decisiones y Dudas

### Decisiones tomadas

* Se eligió un Dashboard Principal como punto de entrada para que el equipo de Customer Success pueda identificar rápidamente las tendencias generales de actividad y adopción.

* Se incluyó un Explorador de Cuentas para facilitar la búsqueda, comparación y priorización de clientes que presentan posibles señales de deterioro.

* Se propuso un Perfil 360 para centralizar la información disponible de cada cuenta y evitar que el usuario tenga que consultar distintas fuentes por separado.

* **Indicadores de actividad:** Se priorizaron métricas como número de chats, mensajes, leads y días activos, ya que permiten observar cambios en el comportamiento de uso de las cuentas.

* **Señales de churn:** Se decidió presentar disminuciones de actividad y patrones de baja adopción como posibles señales de alerta, sin asumir que necesariamente provocan una cancelación.

* **Datos faltantes:** Se decidió diferenciar entre información no disponible y una funcionalidad que realmente no está conectada. Esto es especialmente importante para los indicadores de conexión de canales.

* **Probabilidad de churn:** No se incluyó una puntuación de riesgo generada por un modelo predictivo, ya que no debe presentarse como resultado validado si todavía no se cuenta con un modelo entrenado y evaluado.

* **Diseño para Framework (Streamlit/Dash):** Se organizaron los elementos en bloques de información, tablas y gráficos, manteniendo una barra lateral para la navegación y los filtros principales.

### Dudas / Temas por resolver

* Confirmar cuáles indicadores de adopción y conexión de canales están disponibles para todas las cuentas y cuáles presentan valores faltantes.

* Definir cómo se calcularán y visualizarán los cambios porcentuales de actividad entre meses para evitar comparaciones incorrectas.

* Determinar cómo se tratarán los períodos incompletos, especialmente agosto de 2026, al comparar tendencias de actividad.

* Confirmar qué información de conversaciones y soporte puede integrarse directamente al Perfil 360 y qué indicadores pueden calcularse de manera confiable.

* Definir si posteriormente se incorporará un modelo de Machine Learning para estimar el riesgo de churn, una vez que se cuente con resultados validados.

## Wireframe de la pantalla principal

* **Fidelidad a la estructura del sketch:** Se conservó la distribución base de bloques apilados del sketch (`1440 × 1024 px`), manteniendo la barra lateral fija a la izquierda (`240 px`) para navegación y filtros globales, los 4 indicadores clave (KPIs) en la fila superior, las dos gráficas comparativas en el bloque intermedio y la tabla prioritaria de cuentas con disminución de actividad en la parte inferior.
* **Qué cambió respecto al sketch y por qué:**
  1. Se reemplazaron los rectángulos genéricos por componentes reales compatibles con Streamlit/Dash (`st.selectbox` para filtros, tarjetas `st.metric` con cifra principal y variación porcentual, gráficas con ejes etiquetados y `st.dataframe` con columnas definidas).
  2. Se aplicó jerarquía tipográfica estricta en tres niveles (cifra grande del KPI, títulos de sección y texto de apoyo) con espaciado en múltiplos de 8 (`16 px` y `24 px`) y uso de color acento únicamente en elementos interactivos y alertas de variación negativa.
  3. Se diseñó la pantalla **`Dashboard principal - vacío`** para evitar que la vista parezca rota cuando una combinación de filtros no arroja resultados, incorporando un mensaje claro y un botón de acción directa (`Restablecer filtros`).

## Problemas que aparecieron con contenido real

Al sustituir las etiquetas genéricas por datos y nombres realistas del contexto de **LeadSales**, se detectaron y resolvieron los siguientes problemas:

1. **Valores faltantes vs. ceros reales (Calidad de datos – HO2):** En las banderas de conexión de canales (WhatsApp Web, WhatsApp API, Instagram, Facebook, LeadBot) existe un **30.97% de registros sin información**. Mostrarlos como `0` o `Desconectado` distorsionaba los porcentajes de adopción; se resolvió diferenciando explícitamente el estado *"Información no disponible"* y agregando notas de cobertura en las gráficas.
2. **Períodos incompletos (Agosto 2026):** Los registros del mes en curso (agosto de 2026) no representan un mes cerrado, lo que generaba una caída artificial en la tendencia mensual. Se ajustó el selector de periodo por defecto al último mes cerrado (`Julio 2026`) y se etiquetó el mes parcial en el eje temporal.
3. **Longitud de nombres de cuentas y métricas en tarjetas:** Algunos nombres comerciales largos rompían el ancho de columna en la tabla inferior y las variaciones con decimales saturaban las tarjetas KPI. Se limitó el ancho de la columna `Cuenta` con truncado elegante, se redondearon los porcentajes a un decimal y se trasladaron los filtros secundarios a la barra lateral para mantener la legibilidad a distancia.

## Prueba de los cinco segundos

Se realizó la prueba silenciosa de 5 segundos con un integrante de otro equipo sin darle contexto previo sobre la pantalla:

* **Pregunta 1: ¿Qué crees que hace esta pantalla?**
  * *Respuesta textual:* "Parece ser una plataforma para monitorear la actividad de los clientes e identificar cuáles podrían estar en riesgo de cancelar su servicio."
* **Pregunta 2: ¿Qué fue lo primero que viste?**
  * *Respuesta textual:* "Primero vi los indicadores generales del dashboard y después los gráficos que muestran la actividad de las cuentas."
* **Pregunta 3: ¿Qué harías primero si fueras el usuario?**
  * *Respuesta textual:* "Filtraría por el último mes o revisaría la lista de abajo para ver qué cuentas bajaron más su actividad y abrir su detalle."
* **Ajustes realizados a partir de la prueba:** La jerarquía visual comunicó correctamente el propósito de monitoreo y el recorrido de lectura (KPIs $\rightarrow$ Gráficas $\rightarrow$ Tabla). Como ajuste menor, se dio mayor contraste al encabezado de la tabla inferior (*"Cuentas con mayor disminución de actividad"*) y se añadió una columna de acción (`Ver perfil`) para hacer evidente el paso hacia el **Perfil 360**.

## Pendiente para mañana

* **Pantallas restantes por convertir a wireframe (del Mapa de Sitio):**
  1. `Explorador de cuentas` (completar filas con datos creíbles y botones `Ver perfil`).
  2. `Perfil 360 de la cuenta` (convertir los bloques de texto en tarjetas de métricas reales, indicadores de 3 estados para canales y gráfica de evolución histórica).
  3. `Análisis de adopción` (incorporar ejes reales en las gráficas comparativas activas vs. canceladas y filas de ejemplo en la tabla de deterioro persistente).
* **Preparación para prototipado:** Verificar que todas las pantallas utilicen el mismo componente de barra lateral (`Sidebar`) para conectar la navegación interactiva en la siguiente sesión.

## Prototipo

* **Liga al prototipo navegable (Figma):
* **Recorrido que cubre (basado en el User Flow principal):**
  1. **Flujo principal:** Entrada por `Dashboard principal`luego consulta de KPIs y tabla de caída de actividad  luego clic en `Ver perfil` (ej. cuenta `ACC-1042`) luego navegación hacia `Perfil 360 de la cuenta` luego revisión de canales en 3 estados e historial luego regreso mediante `← Volver` o menú lateral.
  2. **Camino alternativo:** Navegación desde el menú lateral hacia `Explorador de cuentas` luego búsqueda/filtrado de cuenta sospechosa luego apertura de `Perfil 360 de la cuenta`, además de acceso directo a `Análisis de adopción` y prueba de estado vacío (`Dashboard principal - vacío` con botón `Restablecer filtros` funcionando).
  3. **Configuración técnica:** Todas las transiciones utilizan `On click` o `Navigate to` / `Back` con animación `Instant` (compatible con el comportamiento de Streamlit).
* **Qué quedó fuera del prototipo (fuera de alcance):**
  * Combinaciones dinámicas de múltiples filtros simultáneos mostrando subconjuntos distintos de datos (solo se prototipó el caso límite de estado vacío).
  * Paginación individual de todas las páginas del explorador y edición de registros o notas de seguimiento.

## Prueba del prototipo

* **Tarea asignada al usuario:** *"Identifica una cuenta activa que haya tenido una caída fuerte de actividad este mes y revisa qué canales tiene conectados para decidir si requiere seguimiento de Customer Success."
* **Probó:** Vale, Integrante del equipo 4x4 (prueba silenciosa de 8 minutos bajo protocolo *pensar en voz alta*).

### Dónde dudó
* Al abrir el `Perfil 360 de la cuenta`, tardó unos segundos en distinguir si el estado *"Información no disponible"* en Facebook significaba que el cliente había desconectado el canal o que el sistema no tenía registro.
* Intentó hacer clic directamente sobre la fila completa de la cuenta `ACC-1042` en la tabla del `Dashboard principal` antes de notar el enlace `Ver perfil` en la última columna[cite: 17].
* En `Análisis de adopción`, buscó un botón para regresar rápido al `Dashboard principal` dentro del área central antes de mirar la barra lateral.

### Lo que dijo textual
* *"Veo que Clínica Dental Norte bajó 62% en chats; le doy clic aquí en la fila... ah, tengo que darle en 'Ver perfil' a la derecha."
* *"Aquí dice 'Información no disponible' en Facebook; supongo que es porque faltan datos en la base, pero no estoy seguro si lo usan o no."

### Qué vamos a cambiar
* **Filas clicables en tablas:** Conectar la fila completa de las tablas (`Dashboard principal` y `Explorador de cuentas`) además del enlace `Ver perfil` para que ambos lleven al `Perfil 360`.
* **Tooltip / nota aclaratoria en canales:** Hacer más visible la nota explicativa bajo el bloque de canales en el `Perfil 360` (*"Dato sin registro en origen; no implica desconexión"*).
* **Consistencia en navegación:** Mantener siempre resaltada la sección activa en el `Sidebar` y asegurar que el logo superior de `LeadSales` funcione como botón de regreso al `Dashboard principal` desde cualquier pantalla.

## Sound bite

* **Frase elegida (14 palabras):**
  > **"Detecta qué clientes dejan de usar LeadSales hoy, antes de que cancelen mañana."**
* **Otras cuatro alternativas consideradas y descartadas:**[cite: 17]
  1. *"Toda la actividad y adopción de tus cuentas LeadSales en un solo lugar."* (14 palabras — descartada ya que pensabamos que por ser muy descriptiva y poco enfocada en la acción preventiva)
  2. *"Menos horas cruzando archivos, más clientes retenidos a tiempo." (10 palabras la descartamos porque no menciona explícitamente la adopción del producto).
  3. *"Convierte señales de baja adopción en retención proactiva para Customer Success."* (11 palabras la descartamos por sonar demasiado técnica y díficl de entender para los clientes).
  4. *"Identifica cuentas en riesgo de cancelación con datos claros de uso real."* (13 palabras descartada porque la que elegimos comunica mejor la urgencia temporal)

## Elevator pitch

>
> **¿Sabías que muchas cuentas cancelan su suscripción semanas después de dejar de usar funciones clave, sin que nadie lo note a tiempo?** 
>
> Hoy, el equipo de Customer Success en LeadSales tiene los datos de actividad, canales y soporte dispersos, dificultando detectar qué clientes están perdiendo adopción. 
>
> Nuestro monitor centraliza el uso real de cada cuenta, alerta caídas sostenidas de actividad y distingue entre canales desconectados y datos faltantes. 
>
> Diseñamos y validamos cada vista directamente con usuarios reales para priorizar decisiones accionables sin falsas alarmas. 
>
> **¿Nos das 15 minutos esta semana para validar juntos los umbrales de alerta con tu equipo?** 

## Pendientes de diseño

* **Definición formal del umbral de caída de actividad (KPI 4):** Confirmar con el socio formador el criterio matemático exacto (ej. caída $\ge 20\%$ durante 2 meses consecutivos) antes de codificar la métrica.
* **Tratamiento de campos sin cobertura (`Onboarding` y `Sentimiento`):** Validar si se integrarán nuevas fuentes de datos en la fase de desarrollo o si permanecerán con etiqueta explícita de *"No disponible"* en la primera versión funcional.
* **Estados de carga y error:** Diseñar los frames auxiliares (`Loading` y `Error de conexión`) para contemplarlos durante la construcción de la aplicación.