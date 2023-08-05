About
-----
Extension for configuring Flask from environment variables.

Requirements
------------
 * Flask

Installation
------------

::

    pip install flask-envconfig

Usage
-----
Simple usage:

::

    from flask import Flask
    from flask.ext.environ import EnvConfig

    app = Flask(__name__)
    env = EnvConfig(app)

Or, for the application factory pattern:

::

    env = EnvConfig()
    # At a later time
    env.init_app(app)

Now set your configuration variables in your shell, .env file or whatever:

::

    FLASK_DEBUG=True
    FLASK_SECRET_KEY="Something_or_the_other"

By default only environments variables prefixed with FLASK\_ are processed and added to app.config. The extension strips off the prefix so FLASK_DEBUG becomes app.config['DEBUG'] and so forth.
The extension understands "True" to mean True, "False" to mean False and "None" to mean None. It also understands lists, tuples and dicts and numbers.

::

    FLASK_TRUE=True
    FLASK_FALSE=False
    FLASK_NONE=None
    FLASK_INTEGER=1
    FLASK_FLOAT=1.1
    FLASK_STRING="This is a string"
    FLASK_LIST="['a', 'b', 'c']"
    FLASK_TUPLE="('a', 'b', 'c')"
    FLASK_DICT="{'a': 1, 'b': 6}"

The prefix can be changed if so desired:

::

    EnvConfig(app, 'MYPREFIX_')

Or

::

    env = EnvConfig()
    env.init_app(app, 'MYPREFIX_')
