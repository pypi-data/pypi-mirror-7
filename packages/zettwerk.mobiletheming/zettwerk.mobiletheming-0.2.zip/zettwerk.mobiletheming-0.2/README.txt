zettwerk.mobiletheming
======================

Switching mobile themes based on urls


Usage
=====

Install zettwerk.mobiletheming via quickinstaller.
A new control panel entry makes it possible to change settings.

Enter the hostnames on which the mobile theme should be applied.
Choose the diazo theme to use for selected URL.

There is also some settings for "redirecting urls", it works like this:

1) A javascript is installed in portal_javascript
2) This javascript redirects urls to the url set in the control panel.
3) Redirects works for mobile devices.
4) You can choose if you want to redirect iPads and tablets, too.

See this example with the zettwerk.mobile theme: https://www.youtube.com/watch?v=Q2ID86XkiQQ


Generic Setup
=============

This product also provides a GenericSetup extension for integrators to set these settings via a xml profile file. Place the file "mobiletheming.xml" in your (default) generic setup profile and change it as you need. You can also export your current settings via portal_setup -> Export. The export step is called "Mobiletheming Settings".



Example content, taken from `zettwerk.mobile <https://github.com/collective/zettwerk.mobile/tree/master/zettwerk/mobile/profiles/default/mobiletheming.xml>`_::

  <?xml version="1.0"?>
  <settings>
    <themename>zettwerk.mobile</themename>
    <hostnames>
      <element>http://localhost:8080</element>
    </hostnames>
    <ipad>False</ipad>
    <tablets>False</tablets>
  </settings>
