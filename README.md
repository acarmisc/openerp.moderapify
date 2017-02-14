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

Usage
-----

**General informations**

- to specify fields to be retrieved from a ``GET`` method you've to pass ``?fields=id,name,foo,bar``
- if no fields list is specified only ``id`` and ``name`` will be returned
- Requests should have header ``Content-Type application/json``
- At the moment credentials are set in config, in the next update we'll allow performing request as dynamic user (as received from the REST request)

Currently theese actions are supported: 

**Get item data**

Pass ``model`` in dot notation (like ``res.partner``) and the id of item to be retrieved.

    GET /api/<model>/<id>/
    
**Query items**

Call ``api/<model>`` passing ``query`` as semicolon separated list of criteria that Openerp love (ie: field, criteria, value).

    GET /api/<model>/?query=name,like,foo;active,=,true&fields=id,name,bar
    
**Create item**

Not yet implemented

**Edit item**

*Not yet implemented*

**Delete item**

*Not yet implemented*

**Authentication**

*Not yet implemented*

Production deploy
-----------------

To be done
