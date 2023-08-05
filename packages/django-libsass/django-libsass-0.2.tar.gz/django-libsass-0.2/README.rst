django-libsass
==============

A django-compressor filter to compile Sass files using libsass.

Installation
~~~~~~~~~~~~

Starting from a Django project with `django-compressor <https://github.com/django-compressor/django-compressor/>`_ set up::

 pip install django-libsass

and add django_libsass.SassCompiler to your COMPRESS_PRECOMPILERS setting::

 COMPRESS_PRECOMPILERS = (
     ('text/x-scss', 'django_libsass.SassCompiler'),
 )

You can now use the content type text/x-scss on your stylesheets, and have them
compiled seamlessly into CSS::

 {% compress css %}
     <link rel="stylesheet" type="text/x-scss" href="{% static "myapp/css/main.scss" %}" />
 {% endcompress %}


Imports
~~~~~~~

Relative paths in @import lines are followed as you would expect::

 @import "../variables.scss";

Additionally, Django's STATICFILES_FINDERS setting is consulted, and all possible locations
for static files *on the local filesystem* are included on the search path. This makes it
possible to import files across different apps::

 @import "myotherapp/css/widget.scss"


Why django-libsass?
~~~~~~~~~~~~~~~~~~~

We wanted to use Sass in a Django project without introducing any external (non pip-installable)
dependencies. (Actually, we wanted to use Less, but the same arguments apply...) There are a few
pure Python implementations of Sass and Less, but we found that they invariably didn't match the
behaviour of the reference compilers, either in their handling of @imports or lesser-used CSS
features such as media queries.

`libsass <http://libsass.org/>`_ is a mature C/C++ port of the Sass engine, co-developed by the
original creator of Sass, and we can reasonably rely on it to stay in sync with the reference
Sass compiler - and, being C/C++, it's fast. Thanks to Hong Minhee's
`libsass-python <https://github.com/dahlia/libsass-python>`_ project, it has Python bindings and
installs straight from pip.

django-libsass builds on libsass-python to make @import paths aware of Django's staticfiles
mechanism, and provides a filter module for django-compressor which uses the libsass-python API
directly, avoiding the overheads of calling an external executable to do the compilation.

Author
~~~~~~

Matt Westcott matthew.westcott@torchbox.com
