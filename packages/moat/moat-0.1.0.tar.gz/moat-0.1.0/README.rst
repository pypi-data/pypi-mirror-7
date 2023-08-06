Moat
====

Moat provides an elegant way to check and manipulate permissions for Python
objects.

Example
-------

First, mix the UserMixin and ResourceMixin with your User class and the
resources you want to provide authorization for.

.. code-block:: python

    from moat import ResourceMixin, UserMixin

    class Post(ResourceMixin):

        def type(self):
            return self.__class__.__name__

        def identifier(self):
            return self.id


    class User(UserMixin):

        def identifier(self):
            return self.id

Now implement the methods specified in the base Repository class to retrieve
the permissions from the datastore. Pass in an instance of the repository
to the main Moat class.

Now you can check whether a user is actually authorized to do certain things:

.. code-block:: python

    from moat import Moat, Permissions
    from moat.repositories import MockRepository

    moat = Moat(MockRepository())

    # Now you can check if a user has a specific permission for a certain object.
    moat.has(Permission.read, user, post)
    moat.has(Permission.write, user, post)

    # Remove the permission
    moat.remove(Permission.write, user, post)

    # Set the permission, again
    moat.set(Permission.write, user, post)

    # Or get all the ids of type of resources the user has permissions for
    moat.all(Permission.read, user, Post)

