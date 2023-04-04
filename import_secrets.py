import boto3
import json
import argparse

##### Parsing
parser = argparse.ArgumentParser()

parser.add_argument(
    "-r",
    "--region",
    required=False,
    action="store",
    dest="region",
    help="Nombre de la region",
    default=None,
)

parser.add_argument(
    "-c",
    "--cluster",
    required=False,
    action="store",
    dest="cluster",
    help="Nombre del cluster",
    default=None,
)

parser.add_argument(
    "-s",
    "--service-name",
    required=False,
    action="store",
    dest="service",
    help="Nombre de la region",
    default=None,
)

parser.add_argument(
    "-t",
    "--task-definition-file-name",
    required=False,
    action="store",
    dest="task",
    help="Nombre del archivo de la task definition",
    default=None,
)

args = parser.parse_args()

region = args.region
awsClusterName = args.cluster
serviceName = args.service
nomArchivo = args.task


# Configuración de sesión AWS
session = boto3.Session(region_name=region)
parameterStore = session.client('ssm')


prefix = f"/{awsClusterName}/{serviceName}/"


paginator = parameterStore.get_paginator('describe_parameters')
response = paginator.paginate(
    ParameterFilters=[
        {
            'Key': 'Name',
            'Option': 'BeginsWith',
            'Values': [
                prefix,
            ]
        }
    ]
)


parametersList = []

for parameterObtained in response:
    parameterNumber = 0
    while True:
        try:
            parametersList.append(parameterObtained['Parameters'][parameterNumber]['Name'])
            print(f"Agregando {parameterObtained['Parameters'][parameterNumber]['Name']}")
            parameterNumber = parameterNumber + 1
        except:
            break

totalParameters = len(parametersList)
print(f"En total se obtuvieron: {totalParameters} parámetros.")

secretsList = []
# Se forma la lista de objetos a insertar
for param in parametersList:
    shortParam = param.replace(prefix, "")
    paramTuple = ({'name': shortParam, 'valueFrom': param})
    secretsList.append(paramTuple)


# Se abre el archivo como json.
with open(nomArchivo) as fp:
  taskDefinitionJson = json.load(fp)


# Se agrega la lista de secretos en el json.
taskDefinitionJson['containerDefinitions'][0]['secrets'] = secretsList


# Se guarda el json modificado con el mismo nombre y formato.
with open(nomArchivo, 'w') as json_file:
    json.dump(taskDefinitionJson, json_file, 
                        indent=4,  
                        separators=(',',': '))