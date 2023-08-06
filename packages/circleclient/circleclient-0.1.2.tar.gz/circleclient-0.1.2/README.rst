circleclient
============

.. image:: https://travis-ci.org/qba73/circleclient.svg?branch=master
    :target: https://travis-ci.org/qba73/circleclient
    
Python client library for CircleCI API.

Features
========

* Retrieve information about user
* List followed repositories
* Start build
* Cancel build
* Retry build
* Clear build cache


Installation
============

.. code:: python

    pip install circleclient


Usage
=====

Retrieve information about User
-------------------------------

.. code:: python

    import os
    import circleclient
    
    
    token = os.environ['API_TOKEN']
    client = circleclient.CircleClient(api_token=token)
    
    # Retrieve User data
    client.user.get_info()
    

List projects followed by the user
----------------------------------

.. code:: python

   import os
   import circleclient
   
   
   token = os.environ['API_TOKEN']
   client = circleclient.CircleClient(api_token=token)
   
   # Retrieve information about projects
   client.projects.list_projects()
   

Trigger new build in CircleCI
-----------------------------

.. code:: python

   import os
   import circleclient
   
   token = os.environ['API_TOKEN']
   client = circleclient.CircleClient(api_token=token)
   
   # Trigger build
   client.build.triger_new(username='<your_username>', project='<your_project>', branch='<branch>')
   
   
Cancel running build
--------------------

.. code:: python

   import os
   import circleclient
   
   token = os.environ['API_TOKEN']
   client = circleclient.CircleClient(api_token=token)
   
   # Cancel build
   client.build.cancel(username='<your_username>', project='<your_project>', build_num=<build_number>)


Retry build
-----------

.. code:: python

   import os
   import circleclient
   
   token = os.environ['API_TOKEN']
   client = circleclient.CircleClient(api_token=token)
   
   # Rerty build
   client.build.retry(username='<your_username>', project='<your_project>', build_num=<build_number>)

Clear build cache
-----------------

.. code:: python

   import os
   import circleclient

   token = os.environ['API_TOKEN']
   client = circleclient.CircleClient(api_token=token)

   # Clear build cache
   client.cache.clear(username='<your_username>', project='<your_project>')

