#!/usr/bin/env python
import sys
import os
from os.path import dirname, abspath
from optparse import OptionParser

import django
from django.conf import settings


from django.conf import settings


# For convenience configure settings if they are not pre-configured or if we
# haven't been provided settings to use by environment variable.
if not settings.configured and not os.environ.get('DJANGO_SETTINGS_MODULE'):
    settings_dict = dict(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'tests',
        ],
        MIDDLEWARE_CLASSES = (),
        DEBUG = False,
    )

    settings.configure(**settings_dict)
    if django.VERSION >= (1, 7):
        django.setup()


def runtests(*test_args, **kwargs):
    if 'south' in settings.INSTALLED_APPS:
        from south.management.commands import patch_for_test_db_setup
        patch_for_test_db_setup()

    if not test_args:
        test_args = ['tests']
    parent = dirname(abspath(__file__))
    sys.path.insert(0, parent)

    if django.VERSION < (1, 8):
      from django.test.simple import DjangoTestSuiteRunner as TestRunner
    else:
      from django.test.runner import DiscoverRunner as TestRunner

    test_runner = TestRunner(verbosity=kwargs.get('verbosity', 1), interactive=kwargs.get('interactive', False), failfast=kwargs.get('failfast'))
    failures = test_runner.run_tests(test_args)
    sys.exit(failures)

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('--failfast', action='store_true', default=False, dest='failfast')

    (options, args) = parser.parse_args()

    runtests(failfast=options.failfast, *args)