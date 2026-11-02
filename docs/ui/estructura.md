# Estructura de la plataforma - Equipo Teki
 
## Archivo de Figma
https://www.figma.com/design/hqG6A2stQoI7cYATZNNL0J/Laboratorio-6?node-id=0-1&t=u1p3idaJjROVAZ1e-1
 
## Pantallas
1. Portal Principal (Inicio)
Permite al usuario encontrar los servicios disponibles y acceder directamente a la opción de "Obtener Constancia Actualizada", evitando que tenga que buscar el servicio en diferentes portales.

2. Inicio de Sesión Integrado
Permite ingresar las credenciales y completar la verificación CAPTCHA sin perder de vista el trámite seleccionado. Busca mantener la continuidad mediante una autenticación integrada (SSO).

3. Generación de Constancia
Presenta una interfaz simplificada para consultar la información necesaria y generar la constancia actualizada mediante un único botón principal: "Descargar Constancia Actualizada".

4. Gestión de Errores y Ayuda
Proporciona mensajes inmediatos cuando ocurre un error en las credenciales o en el CAPTCHA. Incluye instrucciones contextuales para que el usuario pueda corregirlo sin abandonar el proceso.

5. Descarga de Constancia
Confirma que el documento fue generado y permite al usuario descargar su constancia actualizada.
 
## Trazabilidad con UX
1. Autenticación y acceso directo
- Portal Principal e Inicio de Sesión Integrado
- Redirección directa al servicio seleccionado y autenticación integrada mediante SSO, manteniendo visible el destino del usuario.

2. Simplificación de la interfaz de generación
- Generación de Constancia y Descarga de Constancia
- Eliminación de campos y filtros innecesarios, priorizando una sola acción principal para generar y descargar el documento.

3. Gestión de errores e instructivos contextuales
- Inicio de Sesión Integrado y Gestión de Errores y Ayuda
- Validación de credenciales y CAPTCHA con retroalimentación inmediata, mensajes claros e instrucciones para corregir errores.
 
## Origen de los datos
1. Portal Principal
- **Datos necesarios:** Nombre del servicio y opciones disponibles
- **Origen:** Información institucional del portal; fuente específica por definir.

2. Inicio de Sesión
- **Datos necesarios**: Usuario y contraseña
- **Origen:** Datos ingresados por el usuario.

3. Inicio de Sesión
- **Datos necesarios:** Validación de credenciales
- **Origen:** Sistema de autenticación institucional; integración por definir.

4. Inicio de Sesión
- **Datos necesarios:** CAPTCHA
- **Origen:** Servicio de verificación CAPTCHA; proveedor por definir.

5. Generación de Constancia
- **Datos necesarios:** Información personal del usuario
- **Origen:** Base de datos institucional; por definir.

6. Generación de Constancia
- **Datos necesarios:** Información necesaria para generar la constancia
- **Origen:** Sistema institucional responsable del trámite; por definir.

7. Descarga de Constancia
- **Datos necesarios:** Documento generado
- **Origen:** Sistema de generación de constancias; por definir.

8. Gestión de Errores y Ayuda
- **Datos necesarios:** Mensajes de error e instrucciones
- **Origen:** Reglas de validación y documentación de ayuda; por definir.
 
## Decisiones y dudas
- Se priorizó un acceso directo a "Obtener Constancia Actualizada" desde el portal principal para evitar que el usuario tenga que buscar nuevamente el servicio.
- Se propuso una autenticación integrada para mantener la continuidad entre el portal y el inicio de sesión.
- Filtros avanzados de búsqueda: se excluyeron porque no son necesarios para el flujo principal de descarga y pueden confundir al usuario.
- Pantallas administrativas: no se incluyeron porque el alcance del proyecto se enfoca en la experiencia del usuario que obtiene su constancia.
- Tenemos que: confirmar si el sistema institucional permite implementar autenticación integrada mediante SSO.
- Identificar la base de datos y el sistema del que se obtiene la información necesaria para generar la constancia.