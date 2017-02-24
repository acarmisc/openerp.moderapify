ModernAPIfy
===========

The aim of the product is to create a super-simple RESTful webservice to interact with old OpenERP instances (i.e. 6.1 version) abstracting the ``XML-RPC`` interface with HTTP requests and verbs.

This microservire run with ``klenin`` ( https://github.com/twisted/klein ) that is ``Twisted`` ( https://github.com/twisted/twisted ) based.

Installation
------------

Simply clone the repo and setup your virtual environment ::

    $ git clone https://github.com/acarmisc/openerp.modernapify.git modernapify
    $ cd modernapify
    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install -r requirements.txt

If you want to store credentials locally you can set a db name in ``settings.ini``. To create basic schema run ::

    $ sqlite sessions.db < db.sql


Usage
-----

**General informations**

- to specify fields to be retrieved from a ``GET`` method you've to pass ``?fields=id,name,foo,bar``
- if no fields list is specified only ``id`` will be returned
- Requests should have header ``Content-Type application/json``

**Authentication**

Fire login call and get ``token`` in the response.

    POST /login/

With arguments:

    username=foo
    password=bar

You've to use your token in the next calls like you do in Django Rest Framework or similar:

    Authorization Token 123456asd1234


Currently theese actions are supported:


**Get item data**

Pass ``model`` in dot notation (like ``res.partner``) and the id of item to be retrieved.

    GET /models/<model>/<id>/

**Query items**

Call ``/models/<model>/`` passing ``query`` as semicolon separated list of criteria that Openerp love (ie: field, criteria, value).

    GET /models/<model>/?query=name,like,foo:active,=,true&fields=id,name,bar

**Create item**

Call ``/models/<model>/`` passing fields in the POST payload.

    POST /models/<model>/
        name    =   'Foo'
        counter =   132

**Edit item**

*Not yet implemented*

**Delete item**

*Not yet implemented*

**Call methods**

Call ``/actions/<model>/<method_name>/`` using ``POST`` verb passing:
    - positional arguments in query string or in post body using reserved ``query_params`` as reserved keyword
    - keyword arguments in ``POST`` body

    POST /actions/<model>/<method_name>/?query_params=lorem,ipsum

    foo     = 'Foo'
    bar     = 'Bar'

*Warning:* strange behaviour, arguments in body not working.


Production deploy
-----------------

We provided easy ``start-stop-daemon`` script to be moved inside ``/etc/init.d/`` that act as usual:

    $ /etc/init.d/modernapify start
