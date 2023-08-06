Easymode settings
=================

.. _auto_catalog:

AUTO_CATALOG
------------

Easymode can manage a gettext catalog with your database content for you.
If ``AUTO_CATALOG`` is ``True``, easymode will add every new object of a
model decorated with :class:`~easymode.i18n.decorators.I18n` to the gettext
catalog. The default is ``False``.

How does gettext work
~~~~~~~~~~~~~~~~~~~~~

When existing content is updated in the :ref:`msgid_language` on the
:ref:`master_site`, gettext will try to updated the msgid's in all the languages.
Therefor keeping the mapping between original and translation. There is a limit 
on the ammount of change, before gettext can nolonger identify a string as a 
change in an existing msgid. For example:

.. code-block:: po

    # in the english django.po:
    #: main.GalleryItem.title_text:32
    msgid "I've got a car"
    msgstr ""

.. code-block:: po

    # in the french django.po:
    #: main.GalleryItem.title_text:32
    msgid "I've got a car"
    msgstr "J'ai une voiture"
    
Now we update the main.GalleryItem.title_text in the db in english,
which will also change the english gettext catalog's message id:

.. code-block:: po
    
    # in the english django.po:
    #: main.GalleryItem.title_text:32
    msgid "I've had a car"
    msgstr ""
    
gettext will now also update the message id in french so the link
between original and translation is kept.

.. code-block:: po
    
    # in the french django.po:
    #: main.GalleryItem.title_text:32
    msgid "I've had a car"
    msgstr "J'ai une voiture"
    

The location of the catalog can be controlled using :ref:`locale_dir` and
:ref:`locale_postfix`,

What does AUTO_CATALOG do?
~~~~~~~~~~~~~~~~~~~~~~~~~~

example::

    AUTO_CATALOG = False

With the above settings, no catalogs are managed automatically by easymode. You 
have to manually generate them using :ref:`easy_locale`.

:ref:`auto_catalog` can also be used when you only need *some* (but not all) 
of the internationalised models to auto update the catalog. For this to work
you need to set :ref:`auto_catalog` to ``False`` in settings.py::

    AUTO_CATALOG = False

Then somewhere else, for example in your admin.py or models.py you can turn on
automatic catalog updates for specific models::

    from models import News
    import easymode.i18n
    
    easymode.i18n.register(News)

Now only the ``News`` model will automatically update the catalog, but other models will
leave it alone. See :func:`easymode.i18n.register` for more info.

Ofcourse, for this to work you must have :ref:`master_site` set to ``True``.

In a nutshell, ``MASTER_SITE=False`` will disable all gettext updating, while ``AUTO_CATALOG=False``,
still allows you to turn it on for selected models.

.. _master_site:

MASTER_SITE
-----------

The ``MASTER_SITE`` directive must be set to ``True`` if a gettext catalog 
should be automatically populated when new contents are created. This way all 
contents can be translated using gettext. You can also populate the catalogs
manually using the :ref:`easy_locale` command.

In a multiple site context, you might not want to have all sites updating the
catalog. Because the content created on some of these sites might not need to
be translated because it is not used on any other sites. Content can flow from
'master site' to 'slave site' but not from 'slave site' to 'slave site'.

for more fine grained control over which models should be automatically added
to a gettext catalog, see :ref:`auto_catalog`.

example::

    MASTER_SITE = True

.. _msgid_language:

MSGID_LANGUAGE
--------------

The ``MSGID_LANGUAGE`` is the language used for the message id's in the gettext
catalogs. Only when a content was created in this language, it will be added to
the gettext catalog. If ``MSGID_LANGUAGE`` is not defined, the ``LANGUAGE_CODE``
will be used instead. The msgid's in the gettext catalogs should be the same for 
all languages.

This setting should be used when there are different sites, each with a different 
``LANGUAGE_CODE`` set. These sites can all share the same catalogs.

example::
    
    MSGID_LANGUAGE = 'en'

.. _fallback_langugaes:

FALLBACK_LANGUAGES
------------------

The ``FALLBACK_LANGUAGES`` is a dictionary of values that looks like this::

    FALLBACK_LANGUAGES = {
        'en': [],
        'hu': ['en'],
        'be': ['en'],
        'ff': ['hu','en']
    }

Any string that is not translated in 'ff' will be taken from the 'hu' language.
If the 'hu' also has no translation, finally it will be taken from 'en'.

.. _locale_dir:

LOCALE_DIR
----------

Use the ``LOCALE_DIR`` setting if you want all contents to be collected in a
single gettext catalog. If ``LOCALE_DIR`` is not specified, the contents will
be grouped by app. When a model belongs to the 'foo' app, new contents will be
added to the catalog located in ``foo/locale``.

You might not want to have the dynamic contents written to your app's locale, 
if you also have static translations. You can separate the dynamic and static
content by specifying the :ref:`locale_postfix`.

example::

    PROJECT_DIR = os.dirname(__file__)
    LOCALE_DIR = os.path.join(PROJECT_DIR, 'db_content')
    LOCALE_PATHS = (join(LOCALE_DIR, 'locale'), )

(Note that by using ``LOCALE_PATHS`` the extra catalogs are loaded by django).
    
.. _locale_postfix:

LOCALE_POSTFIX
--------------

The ``LOCALE_POSTFIX`` must be used like this::

    LOCALE_POSTFIX = '_content'

Contents that belong to models defined in the 'foo' app, will be added to the catalog
located at ``foo_content/locale`` instead of ``foo/locale``.

.. _short_language_codes:

USE_SHORT_LANGUAGE_CODES
------------------------

Easymode has some utilities that help in having sites with multiple languages.
``LocaliseUrlsMiddleware`` and ``LocaleFromUrlMiddleWare`` help with adding 
and extracting the current language in the url eg:

http://example.com/**en**/page/1

When having many similar languages in a multi site context, you will have to
use 5 letter language codes:

en-us
en-gb

These language codes do not look pretty in an url:

http://example.com/en-us/page/1

and they might even be redundant because the country code is allready in the domain
extension:

http://example.co.uk/en-gb/page/1

When ``USE_SHORT_LANGUAGE_CODES`` is set to ``True``, the country codes are removed in
urls, leaving only the language code. This means the url would say:

http://example.com/en/page/1

even when the current language would be 'en-us'.

**THIS DIRECTIVE ONLY WORKS WHEN THERE IS NO AMBIGUITY IN YOUR** ``LANGUAGES`` **DIRECTIVE.**

This means i can not have the same language defined twice in my ``LANGUAGES``::

    LANGUAGES = (
        ('en-us', _('American English')),
        ('en-gb', _('British')),
    )

This will **NOT** work because both languages will be displayed in the url as 'en' which is
ambiguous.

SKIPPED_TESTS
-------------

It might be that some tests fail because you've got some modules disabled or you can not comply
to the test requirements. This is very annoying in a continuous integration environment. If you
are sure that the failing tests cause no harm to your application, they can be disabled.

``SKIPPED_TESTS`` is a sequence of test case names eg::

    SKIPPED_TESTS = ('test_this_method_will_fail', 'test_this_boy_has_green_hair')

will make sure these 2 tests will not be executed when running the test suite.

.. _recursion_limit:

RECURSION_LIMIT
---------------

When a model tree is not a dag, easymode can get into an infinite recursion when producing
xml, resulting in a stack overflow. Because xml is produced using :mod:`xml.sax`, which is 
a c-extension, your app will simply crash and not raise any exceptions. Easymode will try 
to help you, by never allowing recursion to go deeper then ``RECURSION_LIMIT``. The default 
is set to::

    RECURSION_LIMIT = sys.getrecursionlimit() / 10

which usually means 100. Take care when increasing this value, because most of the time when
the limit is reached it actually *IS* caused by cycles in your data model and not because of
how many objects you've got in your database.
