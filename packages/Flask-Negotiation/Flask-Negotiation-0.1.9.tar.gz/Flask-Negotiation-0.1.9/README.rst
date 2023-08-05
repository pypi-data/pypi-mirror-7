Flask-Negotiation
=================

Better content-negotiation for flask.

Install
-------

Install with pip

::

    pip install Flask-Negotiation

Usage
-----

Make an app

::

    from flask import Flask
    from flask.ext.negotiation import provides

    app = Flask(__name__)

Make route that provides json only

::

    @app.route('/json')
    @provides('application/json')
    def view():
        return '{"message": "Hi"}'

If request is not acceptable, then it returns HTTP 406 (Not Acceptable)

And you can render data

::

    import json
    from flask.ext.negotiation import Render
    from flask.ext.negotiation.renderers import (renderer, template_renderer,
        json_renderer)

    render = Render(renderers=[template_renderer, json_renderer])

    @app.route('/render')
    def render_view():
        data = get_data()

        ...

        return render(data, 'data/show.html')

It automatically choose renderer by ``Accept`` HTTP Field, and render to
``Response`` object.

For more details, see `documentation`_.

.. _documentation: https://flask-negotiation.readthedocs.org/en/latest/
