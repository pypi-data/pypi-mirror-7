==============
Usage examples
==============

Usage
-----

Import nanolog and log everything like this::

    from nanolog.utils import nanolog

    nanolog('access', 'webinar_detail', request=request)
    nanolog('access', 'webinar_detail', 'Webinar Title', request=request)
    nanolog('changed_password', 'from:x|to:y', 'as we sugested', self.user, '127.0.0.1', log_object)
    nanolog('changed_password', 'from:x|to:y')

ToDO: add more examples here... see also tests.py