django-simple-webservice
========================

Este paquete genera una muy simple interfaz (parecida a json-rpc)
de comunicación con su aplicación.

SETUP
-----

1. Install ``django-summernote`` to your python environment.

::

        pip install django-summernote

2. Add ``django_summernote`` to ``INSTALLED_APP`` in ``settings.py``.

.. code-block:: python

        INSTALLED_APPS += ('simple_webservice', )

3. Add ``django_summernote.urls`` to ``urls.py``.

.. code-block:: python

        urlpatterns = patterns('',
            ...
            url(r'^ws/', include('simple_webservice.urls', namespace='ws')),
            ...
        )

4. Add ``webservice_autodiscover()`` an the top os ``urls.py``

.. code-block:: python

    from simple_webservice import webservice_autodiscover
    webservice_autodiscover()

    urlpatterns = patterns('',
        ...
    )


USAGE
-----

1. create a file ``webservices.py`` inside the app with the webservices

2. Inside the file copy and paste ne next line

.. code-block:: python

    import simple_webservice as ws


3. Puedes agregar las operaciones comunes de sobre los modelos que quieres
   exponer como tus webservices, y puedes restringir el acceso a esos servicios
   por ejemplo, si deseamos darle permiso de lectura al modelo ``User`` del
   sistema de autenticacion de django para que cualquier persona pueda
   consultar a dichos registros pero solo usuarios logueados puedan
   modificarlos podemos escibir algo como:

   .. code-block:: python

        from django.contrib import auth

        import simple_webservice as ws

        ws.register_model(auth.models.User, select=True)
        ws.register_model(auth.models.User, select=True, login=True)


    Pueden darse tambien varios permisos para operaciones en una misma linea
    pero manteniendo los modificadores de acceso iguales. Por ejemplo si
    quisieramos darle todos los permisos para todas las operaciones pero
    sin estarlo logeado al modelo Grupos, podriamos hacer

    .. code-block:: python

        ws.register_model(auth.models.Group, select=True, insert=True,
                          update=True, delete=True, login=True)

4. Otra alternativa es crear webservices mas específicos que representen mas
   la logica de su aplicación. Supongamos que tenemos el siguiente modelo
   en su aplicacion ``foo``

   .. code-block:: python

        class Faa(models.Model):

            some_date = models.DateTimeField()


   Y deseamos hacer un metodo que siempre devuelva los objetos que superen un
   cierto dia en ``some_date``. Podemos crear un webservice con la siguiente
   forma.

   .. code-block:: python

        from foo.models import Faa

        @ws.register_call(login=True)
        def example_webservice(filter_date, *kwargs):
            # the date need to como alwys in iso format
            filter_date = ws.parse_data(
                {"some_date": filter_date}, Faa
            )["some_date"]

            query = Faa.objects.filter(some_date__gte=filter_date)
            return ws.query_to_dict(query)


Como realizar las consultas
---------------------------

Para realizar las consultas usted dispone de  una api uniforme que recive y
emite el formato JSON.

Estas llamadas siempre se encuentran diponible en la url de su aplicación en
el path ``ws/call/``. Por ejemplo si usted esta corriendo su servidor de
desarrollo en localhost y el pueto 8000 las llamadas se recibiran en

::

    http://localhost:8000/ws/call/


La forma de TODA llamada se parece siempre tiene la siguiente estructura:

.. code-block:: javascript

    {
        "id": <null|string|int|bool>,
        "name": "name_of_webservice_to_execute",
        "args": { "arguments of the call" },
        "session": "session id if you are logged in ot null"
    }

El ``id`` solo sirve para identificar llamadas con respuestas

Las respuestas siempre tienen la forma:

      .. code-block:: javascript

          {
            'id': None,
            "stacktrace": "",
            "error": false,
            "response": {"respuesta de la llamada"},
            "error_msg": ""
          }


Las llamadas principales son:

    - ``ping`` Retorna siempre *true* su objetivo es solo saber si el servicio
      funcion.

      **Llamada**

      .. code-block:: javascript

            {
                "id": null,
                "name": "ping",
                "args": {},
                "session": null
            }

      **Respuesta**

      .. code-block:: javascript

          {
            'id': None,
            "stacktrace": "",
            "error": false,
            "response": {"ping": true},
            "error_msg": ""
          }





