# Conexion Power BI con Amazon Athena via ODBC

Esta guia cubre la instalacion del driver ODBC de Athena, la configuracion del DSN en Windows y la conexion desde Power BI Desktop.

---

## 1. Instalar el Simba Athena ODBC Driver

Ve a la pagina oficial de AWS:

```
https://docs.aws.amazon.com/athena/latest/ug/connect-with-odbc.html
```

Descarga el instalador **ODBC 2.x para Windows 64-bit** y ejecutalo con la configuracion por defecto.

---

## 2. Crear el DSN en Windows

Abre el buscador de Windows y busca **"Origenes de datos ODBC (64 bits)"**.

1. Ve a la pestana **DSN de usuario**
2. Clic en **Agregar**
3. Selecciona **Simba Athena ODBC Driver**
4. Clic en **Finalizar**

Completa el formulario con estos valores:

| Campo              | Valor                                      |
|--------------------|--------------------------------------------|
| Data Source Name   | `AthenaVideogames`                         |
| AWS Region         | tu region (ej. `us-east-2`)                |
| Catalog            | `AwsDataCatalog`                           |
| Schema             | `db_videogames`                            |
| Workgroup          | `primary`                                  |
| S3 Output Location | `s3://tu-bucket/athena-results/`           |

---

## 3. Configurar autenticacion

Clic en **Authentication Options** y configura:

| Campo               | Valor                                |
|---------------------|--------------------------------------|
| Authentication Type | `IAM Credentials`                    |
| User                | tu IAM Access Key ID (empieza por `AKIA...`) |
| Password            | tu IAM Secret Access Key             |

> El usuario IAM requerido para esta conexion debe tener las politicas `AmazonAthenaFullAccess` y `AmazonS3FullAccess`. Ver [`docs/iam-user-for-odbc.md`](iam-user-for-odbc.md) para crearlo correctamente.

Clic en **OK** para cerrar Authentication Options.

---

## 4. Probar la conexion

Clic en **Test** en la ventana principal del DSN.

Si el resultado es `SUCCESS! Successfully connected to data source` significa que la conexion esta lista. Clic en **OK** para guardar el DSN.

Si aparece el error `The security token included in the request is invalid`, el problema es que las credenciales usadas pertenecen a un usuario con MFA activo o a una sesion temporal. En ese caso crea un usuario IAM dedicado siguiendo [`docs/iam-user-for-odbc.md`](iam-user-for-odbc.md).

---

## 5. Conectar Power BI Desktop

Abre Power BI Desktop y ve a **Inicio > Obtener datos**.

Busca **Amazon Athena** y seleccionalo. Clic en **Conectar**.

En la ventana de configuracion:

| Campo                    | Valor             |
|--------------------------|-------------------|
| DSN                      | `AthenaVideogames` |
| Modo Conectividad datos  | `Importar`         |

Clic en **Aceptar**.

En la pantalla de autenticacion selecciona **Use Data Source Configuration** y clic en **Conectar**.

En el navegador apareceran las bases de datos y tablas disponibles. Selecciona la tabla `videogames` y clic en **Cargar**.

---

## 6. Cargar consultas SQL nativas

Para cargar cada una de las tres consultas del proyecto como datasets independientes, repite el proceso de **Obtener datos > Amazon Athena** y en el campo **Consulta nativa** pega directamente el contenido del archivo SQL correspondiente de la carpeta `sql/`.

Esto permite construir cada visualizacion sobre datos ya agregados desde Athena, evitando calculos en Power BI.

---

## Notas

- El driver ODBC de Simba solo funciona en Windows. En Mac o Linux se puede usar el conector JDBC de Athena con herramientas compatibles como DBeaver o Tableau.
- Power BI en modo **Importar** descarga los datos al modelo local. Para datasets grandes usa **DirectQuery** para consultar Athena en tiempo real sin descargar datos.
- Athena cobra por datos escaneados (5 GB gratis al mes en Free Tier). El formato Parquet con compresion Snappy reduce drasticamente el volumen escaneado comparado con CSV.
- La autenticacion via IAM Access Keys usada en esta guia es una de las opciones disponibles. Funciona para entornos de aprendizaje y uso personal, pero existen alternativas mas seguras para entornos productivos como roles IAM con sesiones temporales (STS) o AWS IAM Identity Center. Nunca subas tus keys a un repositorio ni las compartas. Si las expones accidentalmente, desactivaras desde IAM de inmediato.
