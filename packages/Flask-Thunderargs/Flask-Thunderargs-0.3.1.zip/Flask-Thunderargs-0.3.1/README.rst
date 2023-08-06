=========
Flask-Thunderargs
=========


Installation
------------

.. code-block:: bash

    sudo pip install flask-thunderargs

Usage
-----

.. code-block:: python

    from flask import Flask
    from flask.ext.thunderargs import ThunderargsProxy
    from thunderargs import Arg

    app = Flask(__name__)
    ThunderargsProxy(app)

    @app.route('/max')
    def find_max(x: Arg(int, multiple=True)):
        return str(max(x))

    if __name__ == '__main__':
        app.run(debug=True)