from extract_transform import extract_transform
from credentials import sql_conection_credentials
from sqlalchemy import create_engine, text

# Credenciales de conexion a la BD
hostname, dbname, uname, pwd = sql_conection_credentials()

# Create SQLAlchemy engine to connect to MySQL Database
engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}"
				.format(host=hostname, db=dbname, user=uname, pw=pwd))

mapa_conexion, accesos_tecnologia_localidad, accesos_velocidad_provincia, velocidad_bajada, penetracion, accesos_bandas, accesos_tipo_conexion, accesos_rango_velocidad, accesos_velocidad_bajada, ingresos_operador, datos_macroeconomicos, provincias, localidades, periodos, data_poblacion = extract_transform()

accesos_tecnologia_localidad = accesos_tecnologia_localidad.merge(localidades).drop(columns=['Total general', 'Link Indec']).melt(id_vars=['Provincia', 'Partido', 'Localidad','Llave'], var_name='Tipo Conexion', value_name='Cantidad').rename(columns = {'Tipo Conexion': 'Tipo'}).drop(columns=['Provincia','Partido','Localidad'])
accesos_velocidad_provincia = accesos_velocidad_provincia.merge(localidades).drop(columns=['Link Indec']).melt(id_vars=['Provincia', 'Partido', 'Localidad', 'Llave'], var_name='Velocidad', value_name='Valor').dropna().drop(columns=['Provincia','Partido','Localidad'])

with engine.connect() as conn:
    accesos_tecnologia_localidad.to_sql('Tecnologia_Provincia', engine, index=True, if_exists='replace')
    accesos_velocidad_provincia.to_sql('Velocidad_Provincia', engine, index=True, if_exists='replace')
    provincias.to_sql('Provincias', engine, index=False, if_exists='replace')
    localidades.to_sql('Localidades', engine, if_exists='replace')
