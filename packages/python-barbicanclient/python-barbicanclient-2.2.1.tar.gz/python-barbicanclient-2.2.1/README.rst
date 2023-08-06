python-barbicanclient
=====================

This is a client for the `Barbican <https://github.com/openstack/barbican>`__
Key Management API.  There is a Python library for accessing the API
(`barbicanclient` module), and a command-line script (`barbican`).

Installation
------------

The client is `pip installable <https://pypi.python.org/pypi/python-barbicanclient>`__ as follows:

.. code:: console

  pip install python-barbicanclient


barbicanclient - Python Library
-------------------------------

The full api is `documented in the wiki <https://github.com/cloudkeep/python-barbicanclient/wiki/Client-Usage>`__.


Here's an example of storing a secret in barbican using the python library
with keystone authentication:

.. code:: pycon

    >>> from barbicanclient.common import auth
    >>> from barbicanclient import client
    >>> # We'll use keystone for authentication
    >>> keystone = auth.KeystoneAuthV2(auth_url='http://keystone-int.cloudkeep.io:5000/v2.0',
    ...                                username='USER', password='PASSWORD', tenant_name='TENANT')
    >>> barbican = client.Client(auth_plugin=keystone)
    >>> # Let's store some sensitive data, Barbican encrypts it and stores it securely in the cloud
    >>> secret_uri = barbican.secrets.store(name='Self destruction sequence',
    ...                                     payload='the magic words are squeamish ossifrage',
    ...                                     payload_content_type='text/plain')
    >>> # Let's look at some properties of a barbican Secret
    >>> secret = barbican.secrets.get(secret_uri)
    >>> print(secret.secret_ref)
    u'http://api-01-int.cloudkeep.io:9311/v1/test_tenant/secrets/49496a6d-c674-4384-b208-7cf4988f84ee'
    >>> print(secret.name)
    Self destruction sequence
    >>> # Now let's retrieve the secret payload.  Barbican decrypts it and sends it back.
    >>> print(barbican.secrets.decrypt(secret.secret_ref))
    the magic words are squeamish ossifrage


barbican - Command Line Client
------------------------------

Command line client configuration and usage is `documented in the wiki <https://github.com/cloudkeep/python-barbicanclient/wiki/Command-Line-Client>`__.

.. code:: console

    $ barbican
    usage: barbican [-h] [--no-auth | --os-auth-url <auth-url>]
                [--os-username <auth-user-name>] [--os-password <auth-password>]
                [--os-tenant-name <auth-tenant-name>] [--os-tenant-id <tenant-id>]
                [--endpoint <barbican-url>]
                <entity> <action> ...

    Command-line interface to the Barbican API.

    positional arguments:
      <entity>              Entity used for command, e.g., order, secret or verification.

    optional arguments:
      -h, --help            show this help message and exit
      --no-auth, -N         Do not use authentication.
      --os-auth-url <auth-url>, -A <auth-url>
                            Defaults to env[OS_AUTH_URL].
      --os-username <auth-user-name>, -U <auth-user-name>
                            Defaults to env[OS_USERNAME].
      --os-password <auth-password>, -P <auth-password>
                            Defaults to env[OS_PASSWORD].
      --os-tenant-name <auth-tenant-name>, -T <auth-tenant-name>
                            Defaults to env[OS_TENANT_NAME].
      --os-tenant-id <tenant-id>, -I <tenant-id>
                            Defaults to env[OS_TENANT_ID].
      --endpoint <barbican-url>, -E <barbican-url>
                            Defaults to env[BARBICAN_ENDPOINT].

    subcommands:
      Action to perform

      <action>
        create              Create a new order.
        store               Store a secret in barbican.
        verify              Begin a verification process in barbican.
        get                 Retrieve a secret, an order or a verification result by providing its URI.
        list                List secrets, orders or verifications.
        delete              Delete a secret, order or verification by providing its href.
