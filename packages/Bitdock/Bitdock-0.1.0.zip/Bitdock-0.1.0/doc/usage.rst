..
    :copyright: Copyright (c) 2014 ftrack

.. _usage:

*****
Usage
*****

Once :ref:`installed <installation>` you need to grab a relevant API token from
Flowdock. Go to https://www.flowdock.com/account/tokens and copy an
appropriate token (for example, a token for a flow called 'Dev'):

.. image:: /image/flowdock_api_token.png

Then start the Bitdock service from the command line passing your copied API
token as the sole parameter:

.. code-block:: bash

    python -m bitdock [YOUR_FLOWDOCK_API_KEY]

.. note::

    To see additional runtime options (such as setting host and port interface)
    use::

        python -m bitdock --help

Now the server is up and running it is time to head over to the Bitbucket
project you want to receive notifications for. Once there, navigate to the
:menuselection:`Settings --> Hooks` page and add a new :guilabel:`Pull Request
POST` hook.

Check only the :guilabel:`Create / Edit / Merge / Decline` option and then
enter the full public URL to your running server adding '/bitbucket-pull-request'
at the end. For example::

     http://example.com:9000/bitbucket-pull-request

.. image:: /image/bitbucket_add_hook.png

Click :guilabel:`Save`.

Now whenever a Bitbucket pull request is created or updated you should see a new
entry in your Flowdock inbox for the configured flow.

.. image:: /image/flowdock_inbox.png

.. note::

    Assigned reviewers will show up as people tags on the inbox entry.

.. _usage/mapping_users:

Mapping Users
=============

As folks may have different user details on Bitbucket and Flowdock there is a
basic way to map from one to the other. Start the server passing in a path to a
JSON file containing mappings or Bitbucket usernames to Flowdock user details.
For example:

:file:`my_mappings.json`

.. code-block:: json

    {
        "martin": {
            "username": "mphillips",
            "display_name": "Martin Pengelly-Phillips",
            "email": "martin@example.com"
        },
        ...
    }

Run the server using:

.. code-block:: bash

    python -m bitdock --user-mapping my_mappings.json
