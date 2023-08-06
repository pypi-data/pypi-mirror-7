****************************************
hyde-gzipper: a gzipping plugin for Hyde
****************************************

hyde-gzipper is a plugin for Hyde, which allows to create
pre-compressed (gzipped) versions after writing output resources.

=====
Usage
=====

In your site.yaml, add this to plugins:

.. code-block:: yaml

    - gzipper.GzipperPlugin

Optionally configure file extensions which you want to include
for compression. Default is: html, css, js.

.. code-block:: yaml

    gzipper:
        extensions:
            - html
            - css
            - js

======
Author
======

`Radek Czajka`_

=======
License
=======

MIT. See LICENSE file.


.. _Radek Czajka: http://rczajka.pl
