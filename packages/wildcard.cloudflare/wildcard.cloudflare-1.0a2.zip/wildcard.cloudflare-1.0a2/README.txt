Introduction
============

This is a very simple package to integrate cloudflare cache purgine
with plone.app.caching.


Usage
-----

- Install "CloudFlare Cache Purging" addon
- Go to "Caching" control panel and make sure "Enable purging" is checked
  in the "Caching proxies" tab.
- Make sure to also configure which content types to enable purging on and
  make sure to check if you are using virtual host urls
- Go to the "CloudFlare" control panel and fill in settings
- Make test purge requests
