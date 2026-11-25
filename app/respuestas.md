# B.1 Predicciones
En primer lugar, aparecerá un separador en el sitio web. A continuación, se crea un contador que comienza en 0, junto con un botón que incrementa el valor en 1 cada vez que se pulsa. Por último, la pantalla mostrará el valor del contador.

1. ¿Por qué el contador nunca pasa de 1, por más veces que presionen el botón?
Annelise: Porque Streamlit vuelve a ejecutar todo el código cada vez que presionamos el botón. Como el contador empieza nuevamente en 0, solamente puede llegar a 1 en cada ejecución.

Arlet: Porque cada vez que hacemos clic, el programa vuelve a empezar desde la primera línea y reinicia el contador en 0. Después suma uno, pero no recuerda el resultado anterior.

Miguel: Esto sucede porque Streamlit ejecuta nuevamente todo el script después de cada interacción. La variable contador se inicializa en 0 cada vez, por lo que al presionar el botón solamente aumenta a 1.

Francesco: Porque el contador se reinicia a 0 cada vez que presionamos el botón. Por eso, siempre vuelve a sumar solamente uno.

2. Si quisieran que el valor se conservara entre una interacción y la siguiente, ¿dónde tendría que guardarse, si no puede ser en una variable normal del script?
Annelise: Tendría que guardarse en un espacio que conserve la información entre ejecuciones, como st.session_state, en lugar de una variable normal.

Arlet: Se tendría que guardar en una variable especial de Streamlit llamada st.session_state, que permite mantener los valores aunque el programa se vuelva a ejecutar.

Miguel: El valor debería almacenarse en st.session_state, ya que funciona como un espacio de almacenamiento que mantiene los datos durante las diferentes interacciones del usuario.

Francesco: En st.session_state, porque permite guardar información sin que se reinicie cada vez que Streamlit ejecuta el código.