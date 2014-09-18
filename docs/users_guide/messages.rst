Messages
========

Google Cloud Endpoints uses `protorpc messages <https://developers.google.com/appengine/docs/python/tools/protorpc/>`__ as the data marshalling library for sending and receiving data v Ferris provides a lot of utilities around defining messages and using them with endpoints.

Most of ferris' message functionality comes from the `protopigeon <https://github.com/jonparrott/protopigeon>`__ library.


Defining messages
-----------------

This is done exactly the same as with the protorpc library::

    from protorpc import messages

    class MyMessage(messages.Message):
        greeting = messages.StringField(1)


Remember endpoints requires that messages used for requests and responses need to be available when a module is imported. This means that you can't create new messages and runtime and expect them to work. Messages should be defined as top-level classes in the module they belong to.


Generating messages from models
-------------------------------

You can generate a message for any ``ndb.Model`` class using ``protopigeon``. All properties, including structured properties, are supported with the exception of computed properties.

For example if you have this model::

    from google.appengine.ext import ndb

    class Post(ndb.Model):
        title = ndb.StringProperty()
        content = ndb.TextProperty()
        favorites = ndb.IntegerProperty()
        created = ndb.DateTimeProperty(auto_now_add=True)


You can generate a message for it::

    import protopigeon

    PostMessage = protopigeon.model_message(Post)


This is equivalent of doing this manually::

    from protorpc import messages
    from protorpc.message_types import DateTimeField


    class PostMessage(messages.Message):
        title = messages.StringField(1)
        content = messages.StringField(2)
        favorites = messages.IntegerField(3)
        created = DateTimeField(4)


Translating between entities and messages
-----------------------------------------

If you have a datastore entity (an instance of a Model) and want to put its data into your generated message::

    post = Post(title="Test post please ignore", content="This is just a test", favorites=1230)
    post_message = protopigeon.to_message(post, PostMessage)

Conversely, if you have an instance of a message and you want an entity::

    post = protopigeon.to_entity(post_message, Post)
    post.put()

You can even use this to update an existing entity instance (this works vice-versa with existing message instances too)::

    Post = Post.query.get()
    protopigeon.to_entity(post_message, post) 


List messages
-------------

Endpoints doesn't allow you to directly return a list of messages. Instead, you need to wrap it in a container message like so::

    PostListMessage(messages.Message):
        items = messages.MessageField(PostMessage, 1, repeated=True)


    posts = Post.query()
    list_message = PostListMessage()
    list_message.items = [protopigeon.to_message(x, PostMessage) for x in posts]


This quickly becomes repetitive. Instead you can use :func:`~protopigeon.list_message` to generate these messages for you::

    PostListMessage = protorpc.list_message(PostMessage)


To simplify the translation part you can use :func:`~ferris3.messages.serialize_list`::

    posts = Post.query()
    list_message = ferris3.messages.serialize_list(PostListMessage, posts)


Composing messages
------------------

Messages can't inherit from other messages, but you can use the :func:`~protopigeon.compose` method to emulate it.::

    class Origin(Message):
        year = IntegerField(1)
        location = StringField(2)

    class Destination(Message):
        name = StringField(1)
        species = StringField(1)

    class Tag(Message):
        urlsafe = StringField(1)

    TravelerWithOriginAndTag = protopigeon.compose(Origin, Destination, Tag)

    instance = TravelerWithOriginAndTag(
        name='The Doctor',
        year=2013,
        location='Gallifrey',
        species='Time Lord',
        urlsafe='the_doctor'
    )


API Reference
-------------


.. function:: protopigeon.model_message(Model, only=None, exclude=None, converters=None)
    
    Generates a protorpc message for the given model. Pass in ``only`` or ``exclude`` to control which fields are present in the generated message.

.. autofunction:: protopigeon.to_message

    Converts the given ``entity`` into a protorpc message using the given ``message`` class.

.. autofunction:: ferris3.messages.serialize

    Alias for :func:`protopigeon.to_message`

.. autofunction:: protopigeon.to_entity

    Converts the given ``message`` into a ndb entity using the given ``model`` class.

.. autofunction:: ferris3.messages.deserialize

    Alias for :func:`protopigeon.to_entity`

.. autofunction:: protopigeon.list_message

    Wraps the given message in a container message that has ``items`` and ``next_page_token`` fields.

.. autofunction:: ferris3.messages.serialize_list

    Transforms all of the provided entities and places it in the message's ``items`` attribute.

.. autofunction:: protopigeon.compose

    Combines two or more messages into one single message class.
