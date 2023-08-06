Changelog
=========

0.3 (2014-08-25)
----------------

.. ATTENTION: currently no upgrade profile for the new properties and javascript
   reinstall needed (which might overwrite your settings for existing properties)

- It is possible to move to a specific slide using a hash in the url.
  (eg. plone/article#slide-5)

- Add z3c.autoinclude entry point for plone

- Show image title in caption text too
  (configurable via ``imageslider_teaser_title``).

- Allow to use plone.app.imaging scales instead of raptus width/height/crop
  settings (via ``images_imagesliderteaser_scale``).

- Responsive Layout by resizing the scrollable via Javascript
  (idea taken from http://cooshtee.com/blog/2013/04/making-jquery-tools-scrollable-responsive/)

  Set Teaser width either via css (``.imageSliderTeaser``) or use the
  ``images_imagesliderteaser_width`` property.

- register Javascript which handles registration of scrollable and events
  for resizing it to be responsive.

0.2 (2013-05-08)
----------------

- slider items can link to other portal content using related items
  (see ``imageslider_teaser_link_related`` in the README)

- pass image object to page-template too, so customized versions can use
  plone.app.imaging scales if the want to.

- only show navigation if there are more than 1 images

- bugfix: images overlapped due to bug in circular implementation.
  wrapping initialization with a timeout fixes the problem

- nicer layout for image captions using rgb() css transparency instead
  of opacity (similar to newsitem_view)


0.1.1 (2012-05-30)
------------------

- fix autoscroll configuration (a typo in `interval`
  prevented the settings to take effect)

0.1 (2012-05-29)
----------------

- initial release [fRiSi]
