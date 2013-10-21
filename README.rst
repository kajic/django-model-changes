====================
django-model-changes
====================

django-model-changes allows you to track the state and changes of a model instance:

Quick start
-----------

1. Install django-model-changes::

    pip install django-model-changes

1. Add "django_model_changes" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'django_model_changes',
    )

2. Add the `ChangesMixin` to your model::

    >>> from django.db import models
    >>> from django_model_changes import ChangesMixin

    >>> class User(ChangesMixin, models.Model):
    >>>     name = models.CharField(max_length=100)

3. Get instance changes::

    >>> user = User()
    >>> user.name = 'Foo Bar'
    >>> user.save()

    >>> user.name 'I got a new name'

    >>> # Get current state
    >>> user.current_state()
    {'id': 1, 'name': 'I got a new name'}

    >>> # Get previous state (state after previous save/create/delete)
    >>> user.previous_state()
    {'id': 1, 'name': 'Foo Bar'}

    >>> # Get old state (state before previous save/create/delete)
    >>> user.old_state()
    {'id': None, 'name': ''}

    >>> # Get changes from the previous state to the current state
    >>> user.changes()
    {'name': ('Foo Bar', 'I got a new name')}

    >>> # Get changes from the old state to the current state
    >>> user.old_changes()
    {'id': (None, 1), 'name': ('', 'Foo Bar')}

    >>> # Check if the instance was persisted (saved)
    >>> user.was_persisted()
    False

    >>> # Check if the instance is persisted
    >>> user.is_persisted()
    True

4. Listen for changes::
        
   >>> from django_model_changes import post_change
    
   >>> def my_callback(sender, instance, **kwargs):
   >>>     # Do something with previous and current state
   >>>     instance.old_state()
   >>>     instance.current_state()

   >>>     # There is also a convenience method to get
   >>>     # an instance from the previous state
   >>>     instance.old_instance()

   >>> post_change.connect(my_callback, User)

Overview
--------

django-model-changes allows you to retrieve the following states from an
instance:

1. current_state()
    The current state of the instance.
2. previous_state()
    The state of the instance **after** it was created, saved or deleted the
    last time.
3. old_state()
    The previous previous_state(), i.e. the state of the instance **before**
    it was created, saved or deleted the last time.

It also provides convenience methods to get changes between states:

1. changes()
    Changes from previous_state to current_state.
2. previous_changes()
    Changes from old_state to previous_state.
3. old_changes()
    Changes from old_state to current_state.

And the following methods to determine if an instance was/is persisted in
the database:

1. was_persisted()
    Was the instance persisted in its old state.
2. is_persisted()
    Is the instance is_persisted in its current state.

This schematic tries to illustrate how these methods relate to each other::


    after create/save/delete            after save/delete                  now
    |                                   |                                  |
    .-----------------------------------.----------------------------------.
    |\                                  |\                                 |\
    | \                                 | \                                | \
    |  old_state()                      |  previous_state()                |  current_state()
    |                                   |                                  |
    |-----------------------------------|----------------------------------|
    |  previous_changes() (prev - old)  |  changes() (cur - prev)          |
    |-----------------------------------|----------------------------------|
    |                      old_changes()  (cur - old)                      |
    .-----------------------------------|----------------------------------.
     \                                                                      \
      \                                                                      \
       was_persisted()                                                        is_persisted()

Limitations
-----------

django-current-changes doesn't track foreign key fields. I plan to add support for it soon.

Documentation
-------------

Refer to the doc strings in `changes.py`_, or build the documentation::

    >>> pip install Sphinx
    >>> cd docs
    >>> make html
    Open build/html/index.html

.. _changes.py: django_model_changes/changes.py
