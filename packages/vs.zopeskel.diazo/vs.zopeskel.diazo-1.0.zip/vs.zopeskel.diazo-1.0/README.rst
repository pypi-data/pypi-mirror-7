=================
vs.zopeskel.diazo
=================

.. contents ::

Introduction
============

`ZopeSkel <https://pypi.python.org/pypi/ZopeSkel>`_ template which allows
individual adaptations of the Bootstrap theme. Therefore it uses `z3c.jbot
<https://pypi.python.org/pypi/z3c.jbot/>`_ to overwrite existing templates
with `z3c.jbot <https://pypi.python.org/pypi/z3c.jbot/>`_. 

Also, you should use Less variables, mixins, etc. Therefore, the
`Buildout <http://www.buildout.org/>`_ configuration file will also install
`Bower <http://bower.io/>`_ and `Grunt <http://gruntjs.com/>`_ to recompile the
bootstrap Less files.

Requirements
============

* This package is only compatible with ZopeSkel<3.0.

Installation
============

Add these lines to your development buildout::

    [buildout]
    parts =
        zopeskel

    [zopeskel]
    recipe = zc.recipe.egg
    unzip = true
    eggs =
        PasteScript
        ZopeSkel
        vs.zopeskel.diazo

Re-run buildout, e.g. with::

    $ ./bin/buildout -c devel.cfg

Create add on
=============

Add ons under development are typically created in your buildout’s ``src``
directory. To add a package named ``my.theme`` you can enter the following
in the terminal::

    $ cd src/
    $ ../bin/zopeskel bootstrap my.theme

This will create a Python package with a directory structure like this::

    my.theme
    ├── bootstrap.py
    ├── buildout.cfg
    ├── docs
    │   ├── INSTALL.txt
    │   ├── LICENSE.GPL
    │   └── LICENSE.txt
    ├── my
    │   └── theme
    │       ├── configure.zcml
    │       ├── diazo_resources
    │       │   ├── favicon.ico
    │       │   ├── img
    │       │   │   ├── apple-touch-icon-144x144-precomposed.png
    │       │   │   ├── apple-touch-icon-57x57-precomposed.png
    │       │   │   ├── apple-touch-icon-72x72-precomposed.png
    │       │   │   ├── apple-touch-icon.png
    │       │   │   └── apple-touch-icon-precomposed.png
    │       │   ├── index.html
    │       │   ├── manifest.cfg
    │       │   ├── preview.png
    │       │   ├── rules.xml
    │       │   └── static
    │       │       ├── css
    │       │       │   └── main.css
    │       │       ├── fonts
    │       │       ├── img
    │       │       └── js
    │       │           └── main.js
    │       ├── Gruntfile.js
    │       ├── interfaces.py
    │       ├── locales
    │       ├── overrides
    │       │   └── plone.app.layout.viewlets.footer.pt
    │       ├── profiles
    │       │   └── default
    │       │       ├── browserlayer.xml
    │       │       ├── cssregistry.xml
    │       │       ├── jsregistry.xml
    │       │       ├── metadata.xml
    │       │       └── theme.xml
    │       └── version.txt
    ├── setup.cfg
    └── setup.py

Generate the theme
==================

To genereate the theme you can switch to your newly created product annd run
buildout, e.g.::

    $ cd src/my.theme
    $ python bootstrap.py
    $ ./bin/buildout

Now you can start the instance and activate ``my.theme`` in *control panel*  →
*Extensions*.

Customize the theme
===================

#. Change the bootstrap css instructions and fonts:

   #. You can customize the bootstrap less variables e.g. in
      ``src/my.theme/my/theme/bower_components/bootstrap/less/variables.less``.
   #. In addition, you can write your own less instructions in
      ``src/my.theme/my/theme/less/custom.less``.
   #. Special fonts can be added in ``/bower_components/bootstrap/dist/fonts/``.
   #. Finally the less files can be recompiled e.g. with::

       $ cd src/my.theme/my/theme
       $ ./node_modules/bower/bin/bower install
       $ ./node_modules/grunt-cli/bin/grunt less
       $ ./node_modules/grunt-cli/bin/grunt copy

#. Change the bootstrap grid:

   The initial grid is defined in ``my/theme/theme/index.html``::

    <div class="container">
      <div class="row">
        <aside id="column-left" class="col-md-3">
          <p>Left column</p>
        </aside>
        <article id="main" class="col-md-6" role="main">
          …
        </article>
        <aside id="column-right" class="col-md-3">
          <p>Right column</p>
        </aside>
      </div>
    </div>

   If you want to define another grid, bootstrap provide many more
   opportunities, see `Bootstrap grid system <http://getbootstrap.com/css/#grid>`_.

#. Overriding templates

   You can easily change templates by copy them into the ``overrides`` folder,
   e.g. from ``eggs/plone.app.layout-2.5.1-py2.7.egg/plone/app/layout/viewlets/footer.pt``
   to ``src/my.theme/my/theme/overrides/plone.app.layout.viewlets.footer.pt``.

Other resources
---------------

``diazo_resources``
^^^^^^^^^^^^^^^^^^^

``diazo_resources/static``
^^^^^^^^^^^^^^^^^^^^^^^^^^

``locales``
^^^^^^^^^^^

``profiles/default``
^^^^^^^^^^^^^^^^^^^^

Usally the files ``public.css``, ``columns.css`` and ``portlets.css`` are not
delivered with yout theme because of the TAL expression
``not: request/HTTP_X_THEME_ENABLED``.  
  
``overrides``
^^^^^^^^^^^^^


