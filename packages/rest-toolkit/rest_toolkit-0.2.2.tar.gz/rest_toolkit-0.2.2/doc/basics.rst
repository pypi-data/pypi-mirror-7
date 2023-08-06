Basic usage
===========

Defining a resource
-------------------

.. code-block:: python

   from rest_toolkit import resource
   from .models import DBSession
   from .models import Event


   @resource('/events/{id:\d+}')
   class EventResource(object):
       def __init__(self, request):
           event_id = request.matchdict['id']
           self.event = DBSession.query(Event).get(event_id)
           if self.event is None:
               raise KeyError('Unknown event id')

As you can see this the `resource` decorator is essentially a convenient way to
setup configure a route with a context factory. It also does a couple of extra
things:

* It add CORS headers to response.
* It adds a default handler for ``OPTIONS`` requests which returns an empty
  response with CORS headers indicating the supported HTTP methods.
* It will return a `HTTP 405 Method Not Supported` response for any requests
  using a method for which no view is defined.


Responding to requests
----------------------

A resource is only useful if it knows how to respond to HTTP requests. This
is done by adding methods and using the ``view`` decorator to inform the system
that they handle a specific HTTP method.

.. code-block:: python

   @EventResource.GET()
   def view(resource, request):
       return {...}


   @EventResource.PUT()
   def update(resource, request):
       return {...}

If a browser sends a ``GET`` request for ``/events/12`` an instance of the
``EventResource`` class is created, and its `view` method is called to
generate a response.


Default views
-------------

If your resource class meets certain requirements rest_toolkit will provide
default views. For example if your resource class is derived from
:py:class:`rest_toolkit.abc.ViewableResource` and implements the `to_dict`
method you automatically get a `GET` view which returns the data returned
by that method.

.. code-block:: python

   from rest_toolkit import resource
   from rest_toolkit.abc import ViewableResource
   from .models import DBSession
   from .models import Event


   @resource('/events/{id:\d+}')
   class EventResource(ViewableResource):
       def __init__(self, request):
           event_id = request.matchdict['id']
           self.event = DBSession.query(Event).get(event_id)
           if self.event is None:
               raise KeyError('Unknown event id')

        def to_dict(self):
            return {'id': self.event.id,
                    'title': self.event.title}

The table below lists the base class you must implement for each
default view.

+--------+------------------------------------------------+
| Method | Class                                          |
+========+================================================+
| DELETE | :py:class:`rest_toolkit.abc.DeletableResource` |
+--------+------------------------------------------------+
| GET    | :py:class:`rest_toolkit.abc.ViewableResource`  |
+--------+------------------------------------------------+
| PATCH  | :py:class:`rest_toolkit.abc.EditableResource`  |
+--------+------------------------------------------------+
| PUT    | :py:class:`rest_toolkit.abc.EditableResource`  |
+--------+------------------------------------------------+


Adding a controller
-------------------

A controller is a special type of resource which is used to trigger an action.
A controller is similar to a button: it does not have any state itself, but it
can modify state of something else. For example a reboot button which will
trigger a server reset. You can define a controller resource manually, but
you can also do so directly on a normal resource using the `controller`
decorator.


.. code-block:: python

   @EventResource.controller(name='reboot')
   def reboot(resource, request):
       return {...}

If you send a ``POST`` to ``/servers/47/reboot`` an instance of the ``Server``
resource will be created, and its ``reboot`` method will be called.
