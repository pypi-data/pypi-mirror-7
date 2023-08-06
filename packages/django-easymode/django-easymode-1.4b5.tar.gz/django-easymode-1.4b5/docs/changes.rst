Release Notes
=============

v1.4b5
------

Fixes compatibity with django 1.7.
Use setuptools instead of distutils.

v1.4b4
------

Fixes Exception in :func:`~easymode.utils.standin.standin_for`: a new-style class can't have only classic bases.

v1.4b3
------

Fixed Django 1.5 template requirements for admin media.

v1.4b2
------

Fixes I18n for models with tuple permissions.
Allow custom admin class for register_all.
fixes wrong import in easymode.tree.admin.forms.

v1.4b1
------

This release fixes most incompatibilities of easymode with django 1.4.
Most importantly, it fixes i18n. This release is therefor meant to be
used with django 1.4.

v1.0b1
------

Easymode is now moving towards the 1.0 release. I took the liberty of removing
code whose usefulness was dubious and also refactor mercilessly. You will
also find some very nice new features in this release!

That being said, you can not simply update and run an existing application on
this release!

Backward incompatible changes:

- The names of localized table columns are constructed differently now. Upgrading means migrating all your column names!
- Easypublisher was removed, because it was too hard to maintain.
- All xml related code moved to the package easmode.tree.xml.
- ``DiocoreCharField``, ``DiocoreHTMLField``, ``DiocoreTextField``, ``CSSField``,
  ``IncludeFileField``, ``RemoteIncludeField`` where removed.

New features:

- New tree module, which uses *real* inlines See :ref:`tree_explanation`.
- You can now hook into xml serialization and have custom serialization for both
  your models as your custom model fields See :ref:`serialize_hook`.

Bugs fixed:

- Fields marked for translation with :class:`~easymode.i18n.decorators.I18n` can
  now be sorted on in the admin when they are included in ``list_display``.
- Order_by now works on translated fields with 5 letter locales::

    from django.utils.languagecode import get_real_fieldname
    
    # this now works:
    MyModel.objects.order_by(get_real_fieldname('somefield', 'en-us'))

v0.14.5
-------

Models decorated with :class:`~easymode.i18n.decorators.I18n` nolonger have problems deleting related models in
cascade mode.

v0.14.4
-------

Easymode nolonger installs any packages automatically during installation, these
should now be installed by hand.

v0.14.3
-------

Using ``super`` in an admin class decorated with L10n, will nolonger result in
infinite recursion.

v0.14.2
-------

Fixes :class:`~easymode.admin.models.fields.SafeHTMLField`'s ``buttons`` property, which can be used to override the tinymce buttons per field.

v0.14.1
-------

ForeignKeyAwareModelAdmin now properly handles parent_link that points to a model
in a different app.

v0.14.0
-------

Added nofollow option to mark foreign keys that shouldn't be followed by the
serializer. Nofollow can be used to optimize easymodes queries when generating
xml, see :ref:`nofollow`. 

v0.13.7
-------

- Fallbacks for translatable fields now also work when the first fallback is not
  the MSGID_LANGUAGE.

v0.13.6
-------

- You can now override the model form of an admin class decorated with L10n, just
  like normal admin classes.

v0.13.5
-------

- Easymode nolonger patches SubFieldBase. Fields that throw Exceptions when their
  descriptor is accessed can now also be internationalized using I18n. This
  includes ImageField and FileField.

v0.13.4
-------

- :func:`~easymode.utils.standin.standin_for` now returns a standin that can be
  pickled and unpickled.

v0.13.3
-------

- register_all will nolonger try to register abstract models
- search_fields is now supported for ModelAdmin classes that use L10n, however it
  will not let you access related items.
- You can now use fieldsets with the *Can edit untranslated fields* permission.
- Added support for creating new objects to easypublisher.
- Added tools to build preview functionality for drafts.
- Added filter that removes unpublished items from the xml.
- fixed error 'cannot import name introspection' caused by a circular import.

v0.10.5
-------

- Added option to exclude models from register_all
- Backwards incompatible change: easymode nolonger has any bindings for 
  django-cms.
- Easymode will now show you the origin of a value, by displaying symbols next to
  the input field in the admin:
  
  1. If a value is from the gettext catalog or fallback, easymode will display **∴°**
  2. If a value is from the database, but the catalog has a different value, easymode will
     display **∴⁺** . You can hover over this symbol to see the catalog value.
  3. If a value is from the database and there is no conflict with the catalog, easymode will
     display only **∴**
- Fixed bug where a value that evaluated to *None* was set with the :class:`string` **None** instead of
  :class:`types.NoneType` :class:`None`
- fixes bug where get_localized_property would crash if settings did not have 
  FALLBACK_LANGUAGES defined.
- :class:`django.db.models.ManyToManyField` and :class:`django.db.models.ForeignKey`
  are now handled by the default xslt ('xslt/model-to-xml.xsl').

v0.9.3
------

- fixes :class:`easymode.admin.abstract.AbstractOrderedModel`
- register_all will ignore models that are :class:`django.contrib.admin.sites.AlreadyRegistered`,
  but still register other models in the module.

v0.9.2
------

- Fixed bug in recursion_depth context manager and added tests.

v0.9.1
------

- Modified the xslt parser to use the file path instead of a string, so you can 
  use xsl:include now.
- libxsltmod is nolonger a supported xslt engine
- Added util to add register all models in some module in one go.

v0.8.6
------

- Easymode will nolonger complain about rosetta, polib and tinymce when none of 
  the features that require these packages are used.
- Moved polib util to :mod:`easymode.utils.polibext` to avoid name clashes 
- :class:`~easymode.admin.models.fields.DiocoreTextField` now accepts cols and rows as parameters.
- The mechanism to add extra attributes to the xml produced by the serializer is 
  now more generic. If a field has the 'extra_attrs' property, these attributes 
  will be added as attributes to the field xml.
- Updated the serializer to support natural keys: 
  http://docs.djangoproject.com/en/dev/topics/serialization/#natural-keys 
- Now easymode can automatically serialize many to many fields. The recursion is 
  guarded, and will let you know when you made a cyclic relation in you model 
  tree. (see :ref:`recursion_limit`).
- :class:`~easymode.utils.mutex` now raises :class:`~easymode.utils.SemaphoreException` instead of doing sys.exit(). 
- When to_python returns a weird object on a field instead of a string, it is now converted to unicode 
  before it is used as a msgid.

v0.6.1
------

- :class:`~easymode.admin.models.fields.DiocoreHTMLField` will now also show a tinymce editor when it
  is not internationalized.
- When there is a problem with monkey patching :class:`django.db.models.SubfieldBase` easymode
  will throw an exception. (Monkey patch fixes http://code.djangoproject.com/ticket/12568).
- New field aded, :class:`~easymode.admin.models.fields.CSSField`, which allows specification of css classes
  for a rich text field, the css classes will appear in the xml as::
  
    style="class1,class2"

v0.6.0
------

- Django 1.2 is required for easymode as of v0.6.0.
- :func:`~easymode.utils.languagecode.get_real_fieldname` now returns 
  a string instead of :class:`unicode`. This way a :class:`dict` can
  be constructed using it's results as keys, and the dict can be turned
  into keyword arguments of ``filter`` when doing a query in a specific
  language.
- Small improvements in error handling when :ref:`auto_catalog` is ``True``

v0.5.7
------

- Added :class:`easymode.admin.models.fields.SafeTextField`, a textfield which strips
  all cariage returns before saving, which is required when using 
  :ref:`auto_catalog_ref`.
- Updated django requirement to v1.1.2 because python 2.6.5 will otherwise
  make the unit tests fail.

v0.5.6
------

- The example app now has a working fixture.

v0.5.5
------

- Special admin widgets are nolonger discarded by easymode (issue #3)

v0.5.4
------

- Some data files where not installed correctly by setup.py

v0.5.3
------

- Added :ref:`auto_catalog` setting, see :ref:`auto_catalog_ref`.
- Fixed error in :ref:`easy_locale` when two properties in the
  same model have the same value (eg. title and subtitle are the same).