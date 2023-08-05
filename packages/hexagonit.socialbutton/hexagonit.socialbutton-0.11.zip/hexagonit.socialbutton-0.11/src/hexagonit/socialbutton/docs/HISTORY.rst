Change log
----------

0.11 (2014-05-13)
=================

- Get rid of portal_url. [taito]
- Need plone.stringinterp>=1.0.11. [taito]

0.10.2 (2013-11-12)
===================

- Bug fix for context which does not have type info. [taito]

0.10.1 (2013-08-08)
===================

- Fix test. [taito]

0.10 (2013-05-01)
=================

- Remove dependency from five.grok. [taito]
- Integrate Travis CI. [taito]
- Move test packages to extras_require. [taito]

0.9 (2012-11-13)
================

- Add permission: **hexagonit.socialbutton: Manage Social Button** to manage social button. [taito]

0.8.1 (2012-09-28)
==================

- Fix bug for multiple line code. [rnd, taito]

0.8 (2012-09-20)
================

- Add dependency to Plone>=4.2.1 and removed dependency to plone.stringinterp>=1.0.7 since Plone-4.2.1 includes it.
  [taito]

0.7 (2012-08-22)
================

- Dependency to plone.stringinterp>=1.0.7 added to make string interpolation available
  in the context of Plone Site root.
  [taito]

0.6 (2012-08-21)
================

- Add guards for cases of None to the upgrade step [rnd]

0.5 (2012-08-17)
================

- Update registry.xml to enable import and export. [taito]
- Switch to use plone.stringinterp instead of format method
  for string interpolation in embedding codes.
  [taito]

0.4 (2012-08-13)
================

- Fixing typo. Po-files initialized. Some translations. [rnd]
- Fixing the problem with some views: guarding the viewlet [rnd]
- google-plus image added [taito]

0.3 (2012-08-08)
================

- Add class for styling against viewlet managers. [rnd]

0.2 (2012-08-02)
================

- Uninstall profile to remove registry records added. [taito]
- UnicodeDecodeError for context title and description fixed for the viewlet. [taito]
- Add 'Plone Site' to the configurable content types. [taito]

0.1 (2012-07-31)
================

- Initial release for use. [taito]

0.0 (2012-07-24)
================

- Initial release. [taito]
