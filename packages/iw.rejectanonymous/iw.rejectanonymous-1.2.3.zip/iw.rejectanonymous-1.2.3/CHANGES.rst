Changes log
===========

1.2.3 (2014-04-30)
------------------

- Modified coding style of getPortalLogoId function.
  [vincentfretin]

- Make iw.rejectanonymous work in tests
  [jaroel]


1.2.2 (2012-08-21)
------------------

- 4.2.1 Compatibility.
  [thomasdesvenain]


1.2.1 (2012-08-16)
------------------

- Include cmf permissions zcml.
  [thomasdesvenain]


1.2 (2012/5/16)
---------------

- ZCML duplicate viewlet setting
  [eleddy]

- Typos in README.rst
  [glenfant]

- Version in setup.py was a float
  [glenfant]


1.1 (2012/5/12)
---------------

- Added doc for customization
  [glenfant]

- Re enabled tests
  [glenfant]

- Disabled some viewlets to anonymous and added doc for customization.
  See https://github.com/collective/iw.rejectanonymous/issues/1
  [glenfant]

- Added valid subpart prefixes such iw.rejectanonymous does not conflict with
  plone.app.theming (Diazo)
  [glenfant]

- Enable portal_kss subparts.
  [thomasdesvenain]

- In plone 4, use of base_properties is sketchy and likely incompat.
  Catch error if needed and use better default for logo.
  [eleddy]


1.0.2 (2010-12-27)
------------------

- z3c.autoinclude awareness added so the ZCML slug does not need to be
  explicitely added in buildout ``*.cfg``.
  [glenfant]

- Add customization utilities and doc (add new enabled ids and subpaths)
  [glenfant]

- Enable favicon.
  [thomasdesvenain]


1.0.1 - 2010-10-08
------------------

- Enable password reset system.
  [thomasdesvenain]


1.0.0 - 2008-02-11
------------------

- Initial release
  [bmathieu]
