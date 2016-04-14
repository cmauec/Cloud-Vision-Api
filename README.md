# Cloud-Vision-Api
Pruebas de Google Cloud Vision API 
https://cloud.google.com/vision/
## Instalación
* Clonar el repositorio
* Activar la facturación en Google Cloud https://console.cloud.google.com/billing
* Activar el API de Google Cloud Vision en https://console.cloud.google.com/apis/library
* Activar el API de Google Translate en https://console.cloud.google.com/apis/library
* Generar clave de cuenta de servicio para el API de Google Cloud en https://console.cloud.google.com/apis/credentials/serviceaccountkey
* Generar Claves de API para la API de Google Translate en https://console.cloud.google.com/apis/credentials/serviceaccountkey
* Creamos una nueva Cuenta de Servicio y bajamos el archivo json, lo guardamos como secret.json
* Copiamos el archivo secret.json en nuestra aplicación de App Engine
* En el archivo main.py en la variable key_google_translate escribimos la clave generada para Google Translate
