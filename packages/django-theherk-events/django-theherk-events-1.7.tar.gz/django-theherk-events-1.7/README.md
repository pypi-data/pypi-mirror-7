TheHerk Events
==============

TheHerk Events is a event posting tool that consists of a Django-cms plugin for showing upcoming events across calendars and has an apphook for viewing calendars and event details.

Usage
-----

1. Add "events" to your INSTALLED_APPS

        INSTALLED_APPS = (
            ...
            'resources',
            'events',
        )

2. Run `python manage.py migrate events`.

   Alternately, you could `syncdb` and `migrate --fake`

Warning
-------

To use the plugin with the default template, you will need to use the apphook, too. The plugin links to a details page in the apphook.

If you intend to use the events plugin without the apphook as well, you will need to override template not to use the URL that points to the apphook.

