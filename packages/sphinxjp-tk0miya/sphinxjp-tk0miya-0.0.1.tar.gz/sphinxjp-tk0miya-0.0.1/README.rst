sphinxjp.tk0miya
=============================

This is a sphinx extension which inserts a flickr photo on your
document.

Setting
=======

Install
-------

::

   $ pip install sphinxjp.tk0miya


Configure Sphinx
----------------

To enable this extension, add ``sphinxjp.tk0miya`` module to extensions
option in `conf.py`.

::

   # Enabled extensions
   extensions = ['sphinxjp.tk0miya']


usage
=====================

::

   .. flickr_search:: marriage


flickr_search put only a first image. You can set `:random:` as option
to put a randomized image.

::

   .. flickr_search:: marriage
      :random:


Config
=========================

You should get access token from Flickr and set filckr_access_token in
your conf.py

::

   flickr_access_token = "<YOUR ACCESS TOKEN PUT HERE>"


Repository
==========

https://bitbucket.org/r_rudi/sphinxjp.tk0miya


License
========

The BSD 2-Clause License.

Note
===============

This extention is created for marriage of "World `tk0miya
<https://twitter.com/tk0miya>`_ ". Congratulations on your wedding!
