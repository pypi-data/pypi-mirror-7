==================
Easy Test Selenium
==================

**Easy Test Selenium** es un mini framework el cual da una propuesta de como debe ser ordenado las pruebas funcionales
y asu vez presenta un marco de trabajo escalable y facil de editar.

Para comenzar a usar **Easy Test Selenium** se debe ejecutar lo siguiente:


    pip install easy_test
    easy_test startproject "nombre de proyecto"


Luego de haber ejecutado estas lineas. Dentro de la carpeta creada, podemos ver que tenemos una carpeta llamada
**principal** y un archivo con el nombre de **manage.py**

El directorio **principal** contiene el archivo de configuración **settings.py**. Este archivo contiene la
configuración de los webdrivers a utilizar, las apps a ser testeadas, entre otros.

Agregando pruebas
-----------------

Necesitamos entrar al proyecto creado y luego ejecutar lo siguiente:


    python manage.py newtest 'prueba_1'


Luego entramos a nuestro archivo settings.py y donde dice WEB_DRIVERS agregamos el webdriver a utilizar indicando
el navegador y el path si lo tuviera.


Ejecutando nuestros tests
-------------------------

Para ejecutar todos nuestros tests ingresamos el siguiente comando:


    python manage.py test all


En caso que deseemos ejecutar solo un test pues indicamos el test en vez indicar all:


    python manage.py 'prueba_1'


La documentación estará próximamente en `FrontEnd Labs <http://frontend-labs.com/>`_.
