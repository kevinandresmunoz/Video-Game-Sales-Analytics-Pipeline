# Usuario IAM dedicado para la conexion ODBC

El driver ODBC de Athena requiere autenticacion mediante IAM Access Keys de largo plazo. Si tu usuario principal de AWS tiene MFA activo o usa roles temporales, la conexion fallara con el error `The security token included in the request is invalid`.

La solucion es crear un usuario IAM dedicado exclusivamente para esta conexion, sin MFA y con permisos minimos.

---

## 1. Crear el usuario

Ve a **IAM > Usuarios > Crear usuario**.

- Nombre de usuario: `powerbi-athena-user`
- No marques la casilla de acceso a la consola de AWS

Clic en **Siguiente**.

---

## 2. Asignar permisos

Selecciona **Adjuntar politicas directamente** y agrega estas dos politicas:

- `AmazonAthenaFullAccess`
- `AmazonS3FullAccess`

Clic en **Siguiente** y luego **Crear usuario**.

---

## 3. Crear las Access Keys

Entra al usuario recien creado, ve a la pestana **Credenciales de seguridad** y clic en **Crear clave de acceso**.

Selecciona el caso de uso **Servicio de terceros**, agrega una descripcion como `odbc-powerbi` y clic en **Crear clave de acceso**.

Copia y guarda en un lugar seguro:

- **Access Key ID** (empieza por `AKIA...`) -> va en el campo **User** del ODBC
- **Secret Access Key** -> va en el campo **Password** del ODBC

> La Secret Access Key solo se muestra una vez. Si la pierdes debes crear una nueva.

---

## 4. Usar las credenciales en el ODBC

En la configuracion del DSN de Simba Athena:

- Clic en **Authentication Options**
- Authentication Type: `IAM Credentials`
- User: el **Access Key ID**
- Password: el **Secret Access Key**

Clic en **Test**. El resultado debe ser `SUCCESS!`.

---

## Consideraciones de seguridad

Este documento describe el uso de IAM Access Keys de largo plazo. Es una de las opciones disponibles para autenticar la conexion ODBC y funciona bien para entornos de aprendizaje o uso personal. Sin embargo, no es el unico metodo ni el mas seguro en todos los contextos. Alternativas que puedes evaluar segun tu caso:

- Roles IAM con sesiones temporales via AWS STS (recomendado para produccion)
- AWS IAM Identity Center (SSO) si tu organizacion lo usa
- Instance profiles si Power BI corre en una EC2 dentro de AWS

Si decides usar Access Keys de largo plazo, ten en cuenta lo siguiente:

- Este usuario tiene permisos limitados a Athena y S3. No puede crear ni eliminar otros recursos de AWS.
- No compartas las Access Keys ni las subas al repositorio. El archivo `.gitignore` del proyecto excluye los patrones de archivos de credenciales mas comunes, pero la responsabilidad final es tuya.
- Nunca pegues las keys directamente en el codigo fuente.
- Si sospechas que las credenciales fueron expuestas, ve a IAM, desactiva las keys comprometidas de inmediato y crea unas nuevas.
- Rota las keys periodicamente como buena practica.
