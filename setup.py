import os
from setuptools import setup, find_packages

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-model-changes',
    version='0.12',
    packages=find_packages(exclude=['tests']),
    license='MIT License',
    description='django-model-changes allows you to track model instance changes.',
    long_description=README,
    url='http://github.com/kajic/django-model-changes',
    author='Robert Kajic',
    author_email='robert@kajic.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    test_suite='runtests.runtests',
    tests_require=[
        'pysqlite',
        'django'
    ],
    zip_safe=False,
)
