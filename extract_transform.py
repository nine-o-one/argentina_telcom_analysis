import pandas as pd
import json
import urllib.request
import credentials

#ACCESO A API
## DATOS DE CONECTIVIDAD A INTERNET EN ARGENTINA
#*Fuente: https://datosabiertos.enacom.gob.ar/dashboards/20000/acceso-a-internet/*

### Leyendo Request a la API
api_key = credentials.api_key()
with urllib.request.urlopen(f'https://api.datosabiertos.enacom.gob.ar/api/v2/resources.json/?auth_key={api_key}') as data2:
    data2 = json.load(data2)

### La API devuelve una lista con los recursos disponibles
recursos = list()
for item in data2:
    recursos.append({'Descripcion': item['description'], 'Titulo': item['title'], 'Categoria': item['category_name'], 'GUID': item['guid'], 'Tipo': item['type']})
recursos = pd.DataFrame(recursos)
datasets = recursos.query('Tipo == "dt"').query('Categoria == "Acceso a Internet"') # Se accede a los recursos que son Datasets de la categoría 'Acceso a internet'

### Se accede a cada recurso y se busca su origen
bucket_s3 = list()
for i, dataset in datasets.iterrows():
    with urllib.request.urlopen(f'https://api.datosabiertos.enacom.gob.ar/api/v2/datasets/{dataset["GUID"]}.json/?auth_key={api_key}') as data:
        data = json.load(data)
    bucket_s3.append({'Titulo': data['title'], 'Descripcion': data['description'], 'GUID': data['guid'], 'URL': data['download_url']})

# EXTRACCIÓN DE S3

normalizacion = {'Ciudad Autónoma de Buenos Aires': 'CABA','Capital Federal': 'CABA', 'Buenos Aires': 'BUENOS AIRES', '24 Partidos del Gran Buenos Aires': 'BUENOS AIRES', 
                 'Resto de partidos de la Provincia\nde Buenos Aires': 'BUENOS AIRES', 'Catamarca': 'CATAMARCA', 'Chaco': 'CHACO', 
                 'Chubut': 'CHUBUT','Córdoba': 'CORDOBA','Corrientes': 'CORRIENTES','Entre Ríos': 'ENTRE RIOS', 'Formosa': 'FORMOSA',
                 'Jujuy': 'JUJUY', 'La Pampa': 'LA PAMPA', 'La Rioja': 'LA RIOJA', 'Mendoza': 'MENDOZA', 'Misiones': 'MISIONES',
                 'Neuquén': 'NEUQUEN', 'Río Negro': 'RIO NEGRO', 'Salta': 'SALTA', 'San Juan': 'SAN JUAN', 'San Luis': 'SAN LUIS',
                 'Santa Cruz': 'SANTA CRUZ', 'Santa Fe': 'SANTA FE', 'Santiago del Estero': 'SANTIAGO DEL ESTERO', 'Santiago Del Estero': 'SANTIAGO DEL ESTERO',
                 'Tierra del Fuego, Antártida e Islas\ndel Atlántico Sur (2)': 'TIERRA DEL FUEGO', 'Tierra Del Fuego': 'TIERRA DEL FUEGO',
                 'Tucumán': 'TUCUMAN'}

def extract_transform():
    mapa_conexion = pd.read_excel(bucket_s3[0]['URL'])
    accesos_tecnologia_localidad = pd.read_excel(bucket_s3[2]['URL'])
    accesos_velocidad_provincia = pd.read_excel(bucket_s3[3]['URL'])
    velocidad_bajada = pd.read_excel(bucket_s3[4]['URL'])
    velocidad_bajada['Provincia'] = velocidad_bajada['Provincia'].replace(normalizacion) # Normalización
    penetracion = pd.read_excel(bucket_s3[1]['URL'], sheet_name='Penetracion-totales')
    accesos_bandas = pd.read_excel(bucket_s3[5]['URL'])
    accesos_bandas['Provincia'] = accesos_bandas['Provincia'].replace(normalizacion) # Normalización
    accesos_tipo_conexion = pd.read_excel(bucket_s3[6]['URL'])
    #accesos_tipo_conexion = accesos_tipo_conexion.drop(columns='Total').melt(id_vars=['Año', 'Trimestre', 'Periodo'], var_name='Tipo Conexion', value_name='No. Conexiones')
    accesos_rango_velocidad = pd.read_excel(bucket_s3[7]['URL'])
    #accesos_rango_velocidad = accesos_rango_velocidad.drop(columns='Total').melt(id_vars=['Año', 'Trimestre'], var_name='Rango', value_name='No. Conexiones')
    accesos_velocidad_bajada = pd.read_excel(bucket_s3[8]['URL'])
    accesos_velocidad_bajada['Provincia'] = accesos_velocidad_bajada['Provincia'].replace(normalizacion)#.melt(id_vars = ['Año', 'Trimestre', 'Provincia'], var_name='Velocidad', value_name='No. Conexiones').dropna()
    ingresos_operador = pd.read_excel(bucket_s3[9]['URL'])
    datos_macroeconomicos = pd.read_excel(bucket_s3[11]['URL'])
    provincias = pd.DataFrame(accesos_bandas['Provincia'].unique()).rename(columns={0:'Provincia'})
    localidades = accesos_tecnologia_localidad[['Provincia','Partido','Localidad']].drop_duplicates()
    localidades['Llave']=localidades.index + 1
    periodos = ingresos_operador.drop(columns=['Ingresos (miles de pesos)'])



    # EXTRACCIÓN DATA DEMOGRÁFICA
    ## DATOS DE POBLACIÓN EN ARGENTICA POR PROVINCIA
    ### CENSO 2022
    #*Fuente https://censo.gob.ar/index.php/datos_provisionales/*

    data_poblacion = pd.read_excel('https://www.indec.gob.ar/ftp/cuadros/poblacion/cnphv2022_resultados_provisionales.xlsx', sheet_name='Cuadro 1')
    data_poblacion.columns = data_poblacion.iloc[1].to_list()
    data_poblacion.drop([0,1,2,5,6,29,30,31,32], inplace=True) # Elimina filas de la tabla que no contienen información
    data_poblacion.reset_index(drop=True, inplace=True)
    data_poblacion['Jurisdicción'] = data_poblacion['Jurisdicción'].replace(normalizacion) # Normalización
    data_poblacion.drop(columns=['Población en situación de calle (vía pública)', 'Población en viviendas colectivas (1)','Total de viviendas colectivas'], inplace=True)
    data_poblacion[['Total de población','Total de viviendas particulares', 'Población en viviendas particulares']]=data_poblacion[['Total de población','Total de viviendas particulares', 'Población en viviendas particulares']].astype('int64') #Convierte tipos
    data_poblacion['Personas por vivienda'] = data_poblacion['Total de población']/data_poblacion['Total de viviendas particulares'].values #Columns calculada

    return mapa_conexion, accesos_tecnologia_localidad, accesos_velocidad_provincia, velocidad_bajada, penetracion, accesos_bandas, accesos_tipo_conexion, accesos_rango_velocidad, accesos_velocidad_bajada, ingresos_operador, datos_macroeconomicos, provincias, localidades, periodos, data_poblacion