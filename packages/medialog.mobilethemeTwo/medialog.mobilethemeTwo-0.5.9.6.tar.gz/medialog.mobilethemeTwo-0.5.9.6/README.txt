medialog.mobilethemeTwo
=======================

WARNING: This product contains a view that could bee a security RISK!

About the theme
===============

A theme intended for use with mobile theming control panel (zettwerk.mobiletheming).
The theme uses plone.app.themingplugins to override templates just for this theme.
These templates will not work if you duplicate the theme TTW (themingplugins do not work for that) 

Nice Icons from IcoMoon is included (GPL or CC BY 3.0) license.

.. image:: https://raw.githubusercontent.com/espenmn/medialog.mobilethemeTwo/master/screenshots_two.png



Usage
======
You probably want to use the theme like this:

- install zettewek.mobiletheming

- install medialog.mobilethemeTwo

- go to the mobile theming control panel and choose which url that should have the mobile theme.

- It is of course possible to enable the theme in diazo theme control panel and use it as a regular theme


When you want to edit the theme, you should do this on the file system.
If you duplicate it TTW, the overridden templates will not be used.




About the views and behavior
============================

- This is very experimental. Please give feedback and suggestions.

- The embed views are probably insecure, if the remote site contains evil code.



How to embed another webpage in your site
=========================================

- go to control panel.

- in the medialog.control panel, set *default settings for your embed views*

- add a dexterity content type

- add  LXML embed behaviour 

- Add a content type to your site and enter embed details

- go to http://plonesite/content/scrape_view 

- You probably want to add the view to the contenttype TTW

 
The view
========

http://yoursite.com/scrape?url=http://plone.org/products/plone/features/


Author
======

Espen Moe-Nilssen, Grieg Medialog AS


