Introduction
============

This is an add-on adapter for `RedTurtle Video`__ product for Plone. For additional documentation see
the main product's page.

Add this to your Plone installation for beeing able to use `YouTube`__ video link as valid
URLs for "Video link" content type.

__ http://plone.org/products/redturtle.video
__ http://www.youtube.com/

Valid URL formats
=================

Classic URL is supported::

    http://www.youtube.com/watch?v=f7OLg1AZvr4&...otherparams

Also the shortened version can be used::

    http://youtu.be/f7OLg1AZvr4

Autoplay
--------

You can enabled the YouTube video autoplay in two ways:

* Use the YouTube ``autoplay=1`` parameter in the YouTube video URL
  you are saving in Plone.
  
  This is a permanent autoplay: the editor choose to autoplay the video at every visit
* Call the RedTurtle video content with the ``autoplay=1`` parameter.
  
  This is a user choice autoplay: who links the Plone content choose to auto
  start it.

In the latter case, some accessibility improvements are added to the page for automatically
put the focus onto the video and simplify keyboard controls (this works on Internet Explorer
and Firefox, probably other browsers also but there isn't a common behavior).

Credits
=======

Developed with the support of:

* `Rete Civica Mo-Net - Comune di Modena`__
  
  .. image:: http://www.comune.modena.it/grafica/logoComune/logoComunexweb.jpg 
     :alt: City of Modena - logo
  
* `Regione Emilia Romagna`__

All of them supports the `PloneGov initiative`__.

__ http://www.comune.modena.it/
__ http://www.regione.emilia-romagna.it/
__ http://www.plonegov.it/

Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.net/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.it/

