Flask-libass
------------

Flask extension for serving css generated from sass or scss.
Uses the bindings to libsass at https://pypi.python.org/pypi/sass/

Example usage:

.. code:: python
    app = Flask(__main__)

    Sass(
        {'main': 'assets/scss/main.scss'}, app,
        url_path='/static/css/',
        include_paths=[
            pkg_resources.resource_filename('other.module', 'assets/scss'),
        ]
    )
