=======
Nanolog
=======

Nanolog is a simple Django app to store simple logs, basically for statistical purposes.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "nanolog" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'nanolog',
    )

2. Run `python manage.py migrate` to create the nanolog models.

Usage
-----

Import nanolog and log everything like this::

    from nanolog.utils import nanolog
    nanolog('changed_password', 'from:x|to:y', 'as we sugested', self.user, '127.0.0.1', log_object)
    nanolog('changed_password', 'from:x|to:y')

Test
----

Just run::

    ./manage.py test nanolog