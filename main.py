import boto3
import requests
import datetime
from botocore.exceptions import ClientError

base_url = "https://api.rm.smartsheet.com/api/v1"
headers = {
    "auth": "********************"
}

def obtener_informacion_api(base_url, headers):
    endpoint = "/assignments"

    try:
        response = requests.get(f"{base_url}{endpoint}", headers=headers)
        response.raise_for_status()

        endpoint = "/assignments"
        url = f"{base_url}{endpoint}"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            datos_api = response.json()
            return datos_api
        else:
            print(f"Error en la petición a la API. Código de estado: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error al hacer la petición a la API: {e}")
        return None, None


def obtener_correo_colaboradores(base_url, headers):
    endpoint = "/users"
    url = f"{base_url}{endpoint}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        datos_correo = response.json()

        if datos_correo is not None:
            correos = []  # Lista para almacenar los correos

            try:
                for usuario in datos_correo['data']:
                    id = usuario['id']
                    correo = usuario['email']
                    name = usuario['display_name']

                    # Agregar el correo a la lista junto con el user_id
                    correos.append({'id': id, 'email': correo, 'name': name})
            except KeyError as e:
                print(f'Error al acceder a la información de correo: {e}')

            return correos  # Retornar la lista de correos
        else:
            print("Error al obtener información de usuarios.")
    else:
        print(f"Error en la petición a la API. Código de estado: {response.status_code}")


def lambda_handler(event, context):
    # Especifica tu región y credenciales aquí
    aws_region = 'us-east-1'
    aws_access_key = '*****************'
    aws_secret_key = '*****************'
    # Obtener información de la API
    api_data = obtener_informacion_api(base_url, headers)
    api_data2 = obtener_correo_colaboradores(base_url, headers)

    fecha_actual = datetime.date.today()
    numero_semana = fecha_actual.isocalendar()[1]
    fecha_actual = datetime.datetime.now()
    meses = {
        "January": "Enero",
        "February": "Febrero",
        "March": "Marzo",
        "April": "Abril",
        "May": "Mayo",
        "June": "Junio",
        "July": "Julio",
        "August": "Agosto",
        "September": "Septiembre",
        "October": "Octubre",
        "November": "Noviembre",
        "December": "Diciembre"
    }
    nombre_mes_ingles = datetime.datetime.now().strftime("%B")

    datos_combinados = []

    # Iterar sobre los proyectos en la primera respuesta
    lista_ids = [elemento['id'] for elemento in api_data2 if 'id' in elemento]

    for persona in api_data['data']:
        user_id = persona['user_id']
        #print(user_id)
        if user_id is not None:  # Verificar si user_id no es None
            if user_id in lista_ids:
                correo = next((elemento['email'] for elemento in api_data2 if elemento['id'] == user_id), None)
                nombre = next((elemento['name'] for elemento in api_data2 if elemento['id'] == user_id), None)
                datos_combinados.append({
                    'Colaborador': nombre,
                    'StartWeek': persona['starts_at'],
                    'EndWeek': persona['ends_at'],
                    'Email': correo,
                    'NumberWeek': datetime.datetime.now().isocalendar()[1],
                    'ActualMonth': meses.get(nombre_mes_ingles, nombre_mes_ingles),
                    'Percent': int(persona['percent'] * 100)
                })
        else:
            pass

    print(datos_combinados)

    # Envío del correo
    try:
        # Crear un nuevo recurso de SES y especificar una región.
        client = boto3.client(
            'ses',
            aws_access_key_id='****************',
            aws_secret_access_key='*****************',
            region_name='us-east-1'
        )

        SENDER = "*******@*********"
        RECIPIENT = "*******@*********"
        AWS_REGION = "us-west-2"
        SUBJECT = "Amazon SES Test (SDK for Python)"
        BODY_TEXT = ("Amazon SES Test (Python)\r\n"
                     "This email was sent with Amazon SES using the "
                     "AWS SDK for Python (Boto)."
                     )

        # Estructura HTML
        BODY_HTML = """<html>
        <head></head>
        <body>
          <h1>Amazon SES Test (SDK for Python)</h1>
          <p>This email was sent with
            <a href='https://aws.amazon.com/ses/'>Amazon SES</a> using the
            <a href='https://aws.amazon.com/sdk-for-python/'>
              AWS SDK for Python (Boto)</a>.</p>
        </body>
        </html>
                    """

        # The character encoding for the email.
        CHARSET = "UTF-8"

        # Create a new SES resource and specify a region.
        client = boto3.client(
            'ses',
            aws_access_key_id='"****************"',
            aws_secret_access_key='"****************"',
            region_name='us-east-1'
        )

        try:
            response = client.send_email(
                Destination={
                    'ToAddresses': [
                        RECIPIENT,
                    ],
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': CHARSET,
                            'Data': BODY_HTML,
                        },
                        'Text': {
                            'Charset': CHARSET,
                            'Data': BODY_TEXT,
                        },
                    },
                    'Subject': {
                        'Charset': CHARSET,
                        'Data': SUBJECT,
                    },
                },
                Source=SENDER,

                #ConfigurationSetName=CONFIGURATION_SET,
            )

        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            print("Email sent! Message ID:")
            print(response['MessageId'])
    except:
        print("Error al obtener información de la API")

if __name__ == "__main__":
    event = {}
    context = {}
    lambda_handler(event, context)
