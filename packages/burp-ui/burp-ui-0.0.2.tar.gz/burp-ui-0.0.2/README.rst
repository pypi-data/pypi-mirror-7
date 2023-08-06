Build Status
------------

.. image:: http://ci.ziirish.me/projects/1/status.png?ref=master
    :target: http://ci.ziirish.me/projects/1?ref=master

Requirements
------------

For LDAP authentication (optional), we need the ``simpleldap`` module that 
requires the following packages on Debian:

::

    aptitude install libsasl2-dev libldap2-dev python-dev


Then we install the module itself:

::

    pip install simpleldap


Installation
------------

Burp-UI is written in Python with the `Flask`_ micro-framework.
The easiest way to install Flask is to use ``pip``.

On Debian, you can install ``pip`` with the following command:

::

    aptitude install python-pip


Once ``pip`` is installed, you can install ``Burp-UI`` this way:

::

    pip install burp-ui


You can setup various parameters in the `burpui.cfg`_ file.
This file can be specified with the ``-c`` flag or should be present in
``/etc/burp/burpui.cfg``.
By default ``Burp-UI`` ships with a default file located in
``$BURPUIDIR/../share/burpui/etc/burpui.cfg``.

Then you can run ``burp-ui``: ``burp-ui``

By default, ``burp-ui`` listens on all interfaces (including IPv6) on port 5000.

You can then point your browser to http://127.0.0.1:5000/

Notes
-----

Please feel free to report any issues on my `gitlab <https://git.ziirish.me/ziirish/burp-ui/issues>`_
I have closed the *github tracker* to have a unique tracker system.

TODO
----

Here is a non-exhaustive list of things I'd like to add:

* server-initiated restoration (with burp, you can create a special file that triggers a restoration when the client contacts the server the next time. In this case the client must accepts server-initiated restoration).
* burp-server configuration front-end (so that you can configure your burp server within burp-ui).
* More statistics.
* etc.

Also note that in the future, I'd like to write a burp-client GUI.
But I didn't think yet of what to do.

Licenses
--------

Burp-UI is released under the BSD 3-clause `License`_.

But this project is built on top of other tools listed here:

- `d3.js <http://d3js.org/>`_ (`BSD <http://git.ziirish.me/ziirish/burp-ui/blob/master/burpui/static/d3/LICENSE>`__)
- `nvd3.js <http://nvd3.org/>`_ (`Apache <http://git.ziirish.me/ziirish/burp-ui/blob/master/burpui/static/nvd3/LICENSE.md>`__)
- `jQuery <http://jquery.com/>`_ (`MIT <http://git.ziirish.me/ziirish/burp-ui/blob/master/burpui/static/jquery/MIT-LICENSE.txt>`__)
- `jQuery-UI <http://jqueryui.com/>`_ (`MIT <http://git.ziirish.me/ziirish/burp-ui/blob/master/burpui/static/jquery-ui/MIT-LICENSE.txt>`__)
- `fancytree <https://github.com/mar10/fancytree>`_ (`MIT <http://git.ziirish.me/ziirish/burp-ui/blob/master/burpui/static/fancytree/MIT-LICENSE.txt>`__)
- `bootstrap <http://getbootstrap.com/>`_ (`MIT <http://git.ziirish.me/ziirish/burp-ui/blob/master/burpui/static/bootstrap/LICENSE>`__)
- `typeahead <http://twitter.github.io/typeahead.js/>`_ (`MIT <http://git.ziirish.me/ziirish/burp-ui/blob/master/burpui/static/typeahead/LICENSE>`__)
- `bootswatch <http://bootswatch.com/>`_ (`MIT <http://git.ziirish.me/ziirish/burp-ui/blob/master/burpui/static/bootstrap/bootswatch.LICENSE>`__)

Also note that this project is made with the Awesome `Flask`_ micro-framework.

Thanks
------

Special Thanks to Graham Keeling for its great software! This project would not
exist without `Burp`_.

.. _Flask: http://flask.pocoo.org/
.. _License: http://git.ziirish.me/ziirish/burp-ui/blob/master/LICENSE
.. _Burp: http://burp.grke.org/
.. _burpui.cfg: http://git.ziirish.me/ziirish/burp-ui/blob/master/burpui.cfg
