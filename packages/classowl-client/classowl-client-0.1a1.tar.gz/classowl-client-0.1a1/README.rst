=============================
Classowl client documentation
=============================

Contents:
=========

This is a client for classowl\'s RESTful API based on slumber,
a generic REST API client. Slumber turns an expression like::

    >>> endpoint.users.me.get(param=2)

or::

    >>> endpoint.users('me').get(param=2)

into an Http request like::

    GET <endpoint>/users/me?param=2

or::

    >>> endpoint.users('me').put(data)

into an Http request like::

    PUT <endpoint>/users/me

It also serializes and deserlializes the data automatically 
to and from dictionaries.

Included are a factory for a slumber endpoint which provides 
authentication given a username and password or an access token::

    >>> import classowl_client
    >>> client = classowl_client.create('username', 'password')
    >>> client.users.me.get()
    DataObject(**{'email': 'you@host.com',
     'first_name': 'John',
     'id': 4387,
     'is_staff': False,
     'last_name': 'Smith',
     'profile': '/api/v1/user_profiles/4381/',
     'resource_uri': '/api/v1/users/4387/',
     'token': '2882386636-c50f9414ae284727fc9e'})

or, if you want to persist the token, avoiding repeating the initial login call::

    >>> token = classowl_client.get_token('username', 'password')
    >>> token
    '78285b2c479c5f9f73ccca094b7f9307f2648144'
    >>> client = classowl_client.create(token=token)
    >>> client.users.me.get()
    DataObject(**{'email': 'you@host.com',
     'first_name': 'John',
     'id': 4387,
     'is_staff': False,
     'last_name': 'Smith',
     'profile': '/api/v1/user_profiles/4381/',
     'resource_uri': '/api/v1/users/4387/',
     'token': '2882386636-c50f9414ae284727fc9e'})

A few lazily instantiated shortcuts to the main endpoints for convenience,
which authenticate using the username and password set on the module::

    >>> classowl_client.username = 'username'
    >>> classowl_client.password = 'password'
    >>> classowl_client.users.me.get()
    DataObject(**{'email': 'you@host.com',
     'first_name': 'John',
     'id': 4387,
     'is_staff': False,
     'last_name': 'Smith',
     'profile': '/api/v1/user_profiles/4381/',
     'resource_uri': '/api/v1/users/4387/',
     'token': '2882386636-c50f9414ae284727fc9e'})

A serializer that turns the received data into objects::

    >>> account = client.users.me.get()
    >>> account
    DataObject(**{'email': 'you@host.com',
     'first_name': 'John',
     'id': 4387,
     'is_staff': False,
     'last_name': 'Smith',
     'profile': '/api/v1/user_profiles/4381/',
     'resource_uri': '/api/v1/users/4387/',
     'token': '2882386636-c50f9414ae284727fc9e'})
    >>> account.last_name
    'Smith'

Its main feature is turning the uri fields into usable endpoints::

    >>> account.profile.get()
    DataObject(**{'avatar_url': None,
     'current_year': None,
     'department': None,
     'email_notifications': True,
     'graduation_year': 2013,
     'id': 4381,
     'is_private': False,
     'is_valid_email': True,
     'resource_uri': '/api/v1/user_profiles/4381/',
     'role': 3,
     'school': '/api/v1/schools/5/',
     'unread_notifications': 40,
     'user': '/api/v1/users/4387/',
     'walkthrough_step': 5})

To update the information::

    >>> account.last_name = 'Brown'
    >>> classowl_client.users.me.put(account)
    DataObject(**{'email': 'you@host.com',
     'first_name': 'John',
     'id': 4387,
     'is_staff': False,
     'last_name': 'Brown',
     'pk': 4387,
     'profile': '/api/v1/user_profiles/4381/',
     'resource_uri': '/api/v1/users/4387/',
     'token': '2882386636-c50f9414ae284727fc9e'})
    >>> classowl_client.users.me.get()
    DataObject(**{'email': 'you@host.com',
     'first_name': 'John',
     'id': 4387,
     'is_staff': False,
     'last_name': 'Brown',
     'profile': '/api/v1/user_profiles/4381/',
     'resource_uri': '/api/v1/users/4387/',
     'token': '2882386636-c50f9414ae284727fc9e'})

You can get the plain dictionary data from it like so::
 
    >>> dict(account)
    {'email': 'you@host.com',
     'first_name': 'John',
     'id': 4387,
     'is_staff': False,
     'last_name': 'Smith',
     'profile': '/api/v1/user_profiles/4381/',
     'resource_uri': '/api/v1/users/4387/',
     'token': '2882386636-c50f9414ae284727fc9e'}
