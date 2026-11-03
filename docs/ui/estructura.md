# Estructura de la Plataforma

## Archivo de Figma

* **Nombre del archivo:** `Equipo Teky - Plataforma de Generación de Constancias`

* **Enlace de Figma:** 

## Pantallas

1. **Portal Principal (Inicio)**

   * **Descripción:** Pantalla de entrada a la plataforma donde el usuario encuentra los servicios disponibles y puede acceder directamente a la opción de "Obtener Constancia Actualizada" sin tener que navegar por otros portales.

   * **Objetivo de UX:** Eliminar la búsqueda dispersa y reducir el número de clics iniciales.

2. **Inicio de Sesión Integrado (SSO)**

   * **Descripción:** Pantalla donde el usuario ingresa sus credenciales y completa la verificación CAPTCHA para acceder al servicio. Mantiene visible el trámite seleccionado y permite una autenticación directa mediante Single Sign-On (SSO).

   * **Objetivo de UX:** Garantizar la continuidad del trámite evitando que el usuario pierda el contexto de la solicitud elegida.

3. **Generación de Constancia**

   * **Descripción:** Pantalla donde el usuario puede consultar su información y generar su constancia actualizada mediante un único botón de acción principal. Presenta una interfaz simplificada, sin filtros ni campos innecesarios.

   * **Objetivo de UX:** Disminuir la sobrecarga cognitiva durante la consulta y generación del documento.

4. **Descarga de Constancia**

   * **Descripción:** Pantalla donde se confirma la generación del documento y se permite al usuario descargar su constancia actualizada.

   * **Objetivo de UX:** Proporcionar una confirmación clara y la entrega inmediata del archivo PDF final.

5. **Gestión de Errores y Ayuda Contextual**

   * **Descripción:** Pantalla que proporciona retroalimentación inmediata cuando ocurre un error en la validación de credenciales o CAPTCHA. Incluye instrucciones contextuales para ayudar al usuario a corregir el problema sin abandonar la plataforma.

   * **Objetivo de UX:** Guiar al usuario paso a paso ante un fallo sin obligarlo a reiniciar todo el proceso.

## Trazabilidad con UX

1. **Autenticación y acceso directo**

   * **Requerimiento atendido:** Acceso sin rodeos al servicio seleccionado.

   * **Pantallas involucradas:** Portal Principal e Inicio de Sesión Integrado.

   * **Justificación / Solución UX:** Redirección directa al servicio seleccionado y autenticación integrada mediante SSO, manteniendo visible el destino del usuario.

2. **Simplificación de la interfaz de generación**

   * **Requerimiento atendido:** Fluidez en la obtención del documento.

   * **Pantallas involucradas:** Generación de Constancia y Descarga de Constancia.

   * **Justificación / Solución UX:** Eliminación de campos y filtros innecesarios, priorizando una sola acción principal para generar y descargar el documento.

3. **Gestión de errores e instructivos contextuales**

   * **Requerimiento atendido:** Prevención de abandono por errores de credenciales o CAPTCHA.

   * **Pantallas involucradas:** Inicio de Sesión Integrado y Gestión de Errores y Ayuda.

   * **Justificación / Solución UX:** Validación de credenciales y CAPTCHA con retroalimentación inmediata, mensajes claros e instrucciones para corregir errores.

## Origen de los Datos

| No. | Pantalla / Bloque | Datos necesarios | Origen del dato / Fuente | 
| ----- | ----- | ----- | ----- | 
| **1** | **Portal Principal** | Nombre del servicio y opciones disponibles | Información institucional del portal (`config/services_catalog.json`) | 
| **2** | **Inicio de Sesión** | Credenciales (Usuario y contraseña) | Datos ingresados por el usuario (`st.text_input`) | 
| **3** | **Inicio de Sesión** | Validación de credenciales | Sistema de autenticación institucional / Proveedor SSO (`OAuth2 / SAML`) | 
| **4** | **Inicio de Sesión** | Verificación CAPTCHA | Servicio externo de verificación CAPTCHA (`reCAPTCHA v3 / hCaptcha`) | 
| **5** | **Generación de Constancia** | Información personal del usuario | Base de datos institucional (`db_usuarios.tb_perfil_contribuyente`) | 
| **6** | **Generación de Constancia** | Información necesaria para generar la constancia | Sistema institucional responsable del trámite (`api/v1/constancias/status`) | 
| **7** | **Descarga de Constancia** | Documento generado | Sistema de generación de constancias (`pdf_generator_service`) | 
| **8** | **Gestión de Errores y Ayuda** | Mensajes de error e instrucciones | Reglas de validación y documentación de ayuda (`config/error_dictionary.py`) | 

## User Flow y Sitemap

### Coherencia de Flujo y Estructura

* **Objetivo del Usuario:** "Quiero consultar y descargar mi constancia actualizada en formato PDF sin perderme en formularios ni trabarme si equivoco mi contraseña."

* **Punto de Dolor Identificado:** Falla o confusión frecuente durante la validación del CAPTCHA o ingreso de credenciales de acceso.

* **Construibilidad (Streamlit/Dash):** Bocetos estructurados estrictamente en filas apiladas y columnas, manteniendo filtros e información del perfil en la barra lateral izquierda (`sidebar`).

### Leyenda de Accesos del Sitemap

*  **Verde (Pública):** Pantalla de entrada accesible a cualquier visitante sin autenticar.

* **Amarillo (Autenticación):** Acceso protegido y validación mediante Single Sign-On (SSO).

* **Azul (Trámite Protegido):** Módulos de consulta, generación y descarga del documento.

* **Rojo (Excepción / Ayuda):** Interfaz para resolución de errores e instrucciones contextuales.

## Decisiones y Dudas

### Decisiones tomadas

* Se priorizó un acceso directo a "Obtener Constancia Actualizada" desde el portal principal para evitar que el usuario tenga que buscar nuevamente el servicio.

* Se propuso una autenticación integrada (SSO) para mantener la continuidad entre el portal y el inicio de sesión.

* **Filtros avanzados de búsqueda:** Se excluyeron porque no son necesarios para el flujo principal de descarga y pueden confundir al usuario.

* **Pantallas administrativas:** No se incluyeron porque el alcance del proyecto se enfoca en la experiencia del usuario que obtiene su constancia.

* **Diseño para Framework (Streamlit/Dash):** Todos los elementos se organizaron verticalmente en bloques apilados para garantizar que se puedan programar mediante layout estándar de filas/columnas.

### Dudas / Temas por resolver

* Confirmar si el sistema institucional permite implementar autenticación integrada mediante SSO (`OAuth2 / SAML`).

* Identificar la base de datos específica y el microservicio backend del que se obtendrá el stream binario para la generación final del archivo PDF.