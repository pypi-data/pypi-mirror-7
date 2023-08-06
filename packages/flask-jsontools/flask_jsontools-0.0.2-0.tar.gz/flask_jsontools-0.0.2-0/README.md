[![Build Status](https://api.travis-ci.org/kolypto/py-flask-jsonapi.png?branch=master)](https://travis-ci.org/kolypto/py-flask-jsonapi)


Flask JsonApi
=============

JSON API tools for Flask

Table of Contents
=================

View Utilities
==============

@jsonapi
--------

Decorate a view function that talks JSON.

Such function can return:
    
* tuples of `(response, status[, headers]): to set custom status code and optionally - headers
* Instances of [`JsonResponse`](#jsonresponse)
* The result of helper function [`make_json_response`](#make_json_response)

Example:

```python
from flask.ext.jsontools import jsonapi

@app.route('/users')
@jsonapi
def list_users():
    return [
        {'id': 1, 'login': 'kolypto'},
        #...
    ]
   
@app.route('/user/<int:id>', methods=['DELETE'])
def delete_user(id):
    return {'error': 'Access denied'}, 403
```

### JsonResponse

Extends [`flask.Request`](http://flask.pocoo.org/docs/api/#incoming-request-data) and encodes the response with JSON.
Views decorated with [`@jsonapi`](#jsonapi) return these objects.

Methods:

* `preprocess_response_data(response)`: Override to get custom response behavior.
* `get_json()`: Get the original response data.
* `__getitem__(key)`: Get an item from the response data

The extra methods allows to reuse views:

```python
from flask.ext.jsontools import jsonapi

@app.route('/user', methods=['GET'])
@jsonapi
def list_users():
    return [ { 1: 'first', 2: 'second' } ]
    
@app.route('/user/<int:id>', methods=['GET'])
@jsonapi
def get_user(id):
    return list_users().get_json()[id]  # Long form
    return list_users()[id]  # Shortcut
```

JsonExcApi
----------

Decorator base class which helps to create API views which can report errors to the client.

However, it won't just magically report all exceptions: you need to override its `exception()` method and declare how errors should be formatted:

```python

from werkzeug.exceptions import HTTPException, NotFound
from flask.ext.jsontools import JsonExcApi

class jsonapi(JsonExcApi):
    """ Custom @jsonapi with error formatter """
    def exception(self, e):
        if isinstance(e, HTTPException):
            # Return error object, and set HTTP code by returning a tuple
            return {'error': dict(
                name=type(e).__name__,
                title=e.name,
                message=e.description
            )}, e.code
        elif isinstance(e, RuntimeError):
            # Return error object, http code will be 200
            return {'error': dict(
                name=type(e).__name__,
                title=type(e).__name__,
                message=e.message
            )}
        # Otherwise, the error is raised
        return None

@app.route('/error')
@jsonapi
def error():
    raise NotFound('Nothing found')
```

A request to `/error` will result in the following JSON response:
    
    {'name': 'NotFound', 'title': 'Not Found', 'message': 'Nothing'}



JsonClient
==========

JsonClient is a JSON-aware test client: it can post JSON and parse JSON responses into [`JsonResponse`](#jsonresponse).

```python
from myapplication import Application
from flask.ext.jsontools import JsonClient

def JsonTest(unittest.TestCase):
    def setUp(self):
        self.app = Application(__name__)
        self.app.test_client_class = JsonClient
        
    def testCreateUser(self):
        with self.app.test_client() as c:
            rv = c.post('/user/', json={'name': 'kolypto'})
            # rv is JsonResponse
            rv.status_code
            rv.get_json()['user']  # Long form for the previous
            rv['user']  # Shortcut for the previous
```
