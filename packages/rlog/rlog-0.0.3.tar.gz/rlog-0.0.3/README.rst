rlog
====

Small handler and formatter for using python logging with Redis. This is
cleared and simplified version of
`python-redis-log <https://github.com/jedp/python-redis-log>`__ by Jed
Parsons, with Python3 support.

Installation
------------

The current stable release:

::

    pip install rlog

or:

::

    easy_install rlog

or from source:

::

    $ sudo python setup.py install

Usage
-----

::

    >>> from rlog import RedisHandler
    >>> logger = logging.getLogger()
    >>> logger.addHandler(RedisHandler(channel='test'))
    >>> logger.warning("Spam!")
    >>> logger.error("Eggs!")

Redis clients subscribed to ``test`` will get a json log record.

You can use the ``redis-cli`` shell that comes with ``redis`` to test
this. At the shell prompt, type ``subscribe my:channel`` (replacing with
the channel name you choose, of course). You will see subsequent log
data printed in the shell.

Also you can use it with Django:

.. code:: Python

        LOGGING = {
            'version': 1,
            'disable_existing_loggers': True,
            'handlers': {
                'redis': {
                    'level': 'DEBUG',
                    'class': 'rlog.RedisHandler',
                    'host': 'localhost',
                    'password': 'redis_password',
                    'port': 6379,
                    'channel': 'my_amazing_logs'
                }
            },
            'loggers': {
                'django': {
                    'level': 'INFO',
                    'handlers': ['redis'],
                    'propagate': True,
                },
            }
        }

You can also simply use it with logstash.

