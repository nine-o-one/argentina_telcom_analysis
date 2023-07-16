
![logo Henry](https://www.soyhenry.com/_next/image?url=https%3A%2F%2Fassets.soyhenry.com%2Fhenry-landing%2Fassets%2FHenry%2Flogo.png&w=128&q=75)

# **ARGENTINA TELECOMUNICATIONS ANALYSIS** - Henry

## **¿Por qué existe este proyecto?**

Este proyecto tiene como objetivo realizar el ETL y análisis exploratorio de los datos disponibles sobre telecomunicaciones en Argentina, entregando un informe general sobre las perspectivas de mercado y posibles escenarios futuros. 

Este análisis se apalanca en un dashboard de PowerBI conectado a una base de datos MySQL, y hace parte del proyecto individual de [@soyhenry_ok](https://twitter.com/soyhenry_ok).

## ETL

### Extracción y Transformación

La fuente de datos principal para este análisis son los [datos abiertos](https://datosabiertos.enacom.gob.ar/dashboards/20000/acceso-a-internet/) publicados por ENACOM (Entre regulador de comunicaciones y medios en argentina).

El módulo ```extract_tranform.py``` realiza la conexión, extracción y transformación de las fuentes de datos de la siguiente manera:

1. Realiza una solicitud GET a la [API de ENACOM](https://datosabiertos.enacom.gob.ar/developers/) la cual retorna todos los recursos disponibles para esta aplicación.
2. Filtra todos los recursos que son de tipo *Datasets* y que corresponden a la categoría *Acceso a internet* almacenandolos en un DataFrame.
3. Reliza nuevamente una solicitud GET por cada uno de los recursos disponibles, obteniendo la URL de acceso al bucket de AWS S3 donde se encuentra almacenado dicho recurso.
4. Utilizando Pandas, realiza la solicitud del recurso al bucket de S3 y lo almacena en un DataFrame.
5. Utilizando Pandas, realiza la solicitud del archivo .xls disponible en el servidor del [INDEC](https://censo.gob.ar/index.php/datos_provisionales/) y lo almacena en un DataFrame.

La tranformación de los datasets rescatados se realiza de la siguiente manera:

1. Se normaliza la *Provincia* en todos los dataset que contienen esta dimesión, utilizando un diccionario base con todas las tranformaciones, el cual se mapea en cada DataFrame correspondiente.
2. Se crean las tablas de dimensión ```provincias```, ```localidades``` y ```periodos``` para se utilizadas en el modelo de datos del dashboard.
3. Se ajusta el nombre de las columnas y se eliminan las columnas no deseadas de los DataFrames.

### Carga

La carga de los datos transformados se realiza a una base de datos MySQL propia, la cual se utiliza como fuente de datos para la consturcción del Dashboard, utilizando el módulo ```load.py```. La conexión a la base de datos se realiza utilizando SQLAlchemy y el paquete de conexión pymysql.

## EDA

### Comportamiento de conexiones a internet 2014 a 2022

Entre el 2014 y el 2022, el número de conexiones a internet en argentina ha crecido un 73,3%, **pasando de poco más de 6 millones en 2014 a más de 11 millones en el tercer trimestre de 2022**. Las conexiones Cablemódem se han convertido en el principal tipo de conexión con más de 6 millones de conexiones activas para 2022, ésto gracias a su facil despliegue, bajo costo y mejora en el ancho de banda comparado con la técnología ADSL.

Sin embargo, desde 2018 con el início del despliegue de redes con tecnología de Fibra óptica domiciliarias, se ha iniciado la migración tecnológica acompañada de un incremento en la velocidad contratada, debido principalmente al relevo generacional de los Milenials que trae consigo nuevos hábitos de consumo digitales (Streaming, Gaming, Redes Sociales, entre otros). 

![plot1](/img/g1.png)

Por otra parte, aunque el número de conexiones a internet sigue creciendo, argentina (con 76.6 conexiones por cada 100 hogares) continúa por debajo del promedio en América Continental que se encuntra en 81.4 conexiones por cada 100 hogares en 2021<sup>[1](#nota1)</sup>. Este panorama es incluso peor frente a la adopción de fibra óptica domiciliaria, donde Argentina se encuentra en último lugar con solo el 20,2 por debajo incluso de paises vecinos como Chile y Brassil<sup>[2](#nota2)</sup> debido a las fuertes regulaciones existentes y el DNU de regulación de precios<sup>[3](#nota3)</sup>. 

![plot2](/img/g2.png)

 <sup><a href="#nota1">1</a></sup> : https://es.statista.com/estadisticas/598732/hogares-con-acceso-a-internet-en-el-mundo-por-region

 <sup><a href="#nota2">2</a></sup> : https://www.iprofesional.com/tecnologia/368248-conexiones-de-fibra-optica-cual-es-el-puesto-de-argentina

 <sup><a href="#nota3">3</a></sup> : https://www.iprofesional.com/tecnologia/369795-obstaculos-el-largo-camino-de-la-fibra-optica-en-argentina

### Velocidad de conexión

A partir de 2018, **la velocidad máxima de bajada ha crecido de forma sostenida a un ritmo cercano a los 20 Mbps por año.** Sin embargo, el mayor número de conexiones de alta velocidad se encuentra en los centros poblados donde se ha realizado el despliegue de redes de Fibra ótica, como Caba, Buenos Aires, Cordoba y Tucuman.

![plot3](/img/g3.png)

### Distribución demografíca

La mayor parte de la población se distribuye en los grandes centros poblados como Buenos Aires, Cordoba, Santa Fe y CABA. En promedio, hay 2,5 personas por cada vivienda particular, sin embargo, este promedio es mucho menor en CABA donde hay  solo 1,9 personas por cada vivienda particular. 

|    | Total |
| ----------- | ----------- |
| Viviendas particulares | 17.780.210 |
| Población | 46.044.703 |
| Población en viviendas particulares | 45.767.858 |

<sup>*Censo Nacional de Población, Hogares y Viviendas 2022 - 
Resultados provisionales - INDEC*</sup>

Este fenómeno se da en gran medida como resultado de la devaluación del metro cuadrado de vivienda en el área<sup>[4](#nota4)</sup> y la tendencia creciente a hogares unipersonales como poryecto de vida de los Milenials.

 ![plot4](/img/g4.png)

 <sup><a href="#nota4">4</a></sup>: https://www.infobae.com/economia/2022/06/19/mercado-inmobiliario-en-que-barrios-portenos-bajaron-mas-los-precios-de-los-departamentos/

### Ingresos generados por operadores

Los ingresos generados por la prestación del servicio de internet, son directamente proporcionales a la penetración del servicio a nivel nacional. 

Sin embargo, para 2019 con un escenario inflacional sin presedentes<sup>[5](#nota5)</sup> los operadores incrementaron significativamente los precios del servicio<sup>[6](#nota6)</sup> manteniendo el crecimiento en sus ingresos a pesar de haber una disminución en el número de usuarios activos.

No se encuentra ninguna relación entre el precio del dolar y los ingresos de los operadores, ya que las cuentas se cobran en pesos argentinos. Sin embargo, **la variación del precio del dolar impacta negativamente la inversión en infraestructura de telecomuniaciones** ya que le mayor parte de los insumos requeridos para los proyectos de modernización son importados.

 ![plot5](/img/g5.png)

 <sup><a href="#nota5">5</a></sup> : https://elpais.com/economia/2020/01/15/actualidad/1579119241_444665.html

 <sup><a href="#nota6">6</a></sup> : https://www.lanacion.com.ar/tecnologia/segun-indec-servicios-telefonia-movil-internet-aumentaron-nid2325651

