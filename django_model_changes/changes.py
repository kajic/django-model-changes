import copy
from mongoengine import signals
from .signals import post_change

SAVE = 0
DELETE = 1


class ChangesMixin(object):
    """
    ChangesMixin keeps track of changes for model instances.

    It allows you to retrieve the following states from an instance:

    1. current_state()
        The current state of the instance.
    2. previous_state()
        The state of the instance **after** it was created, saved
        or deleted the last time.
    3. old_state()
        The previous previous_state(), i.e. the state of the
        instance **before** it was created, saved or deleted the
        last time.

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

    This schematic tries to illustrate how these methods relate to
    each other::


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
        .----------------------------------------------------------------------.
         \                                                                      \
          \                                                                      \
           was_persisted()                                                        is_persisted()

    """

    def __init__(self, *args, **kwargs):
        self._states = []
        
        if not hasattr(self, '_data'):
            self._data = {}

        if not 'id' in kwargs:
            self._save_state(new_instance=True)

        super(ChangesMixin, self).__init__(*args, **kwargs)

        if self.id:
            self._save_state(new_instance=True)

        signals.post_save.connect(
            _post_save, sender=self.__class__,
            # dispatch_uid='django-changes-%s' % self.__class__.__name__
        )
        signals.post_delete.connect(
            _post_delete, sender=self.__class__,
            # dispatch_uid='django-changes-%s' % self.__class__.__name__
        )

    def _save_state(self, new_instance=False, event_type='save'):
        # Pipe the pk on deletes so that a correct snapshot of the current
        # state can be taken.
        if event_type == DELETE:
            self.pk = None

        # Save current state.
        self._states.append(self.current_state())

        # Drop the previous old state
        # _states == [previous old state, old state, previous state]
        #             ^^^^^^^^^^^^^^^^^^
        if len(self._states) > 2:
            self._states.pop(0)

        # Send post_change signal unless this is a new instance
        if not new_instance:
            post_change.send(sender=self.__class__, instance=self, changes=self.old_changes())

    def current_state(self):
        """
        Returns a ``field -> value`` dict of the current state of the instance.
        """
        def _try_copy(v):
            if isinstance(v, (list, dict)): return copy.copy(v) # Shallow copy
            return v
        
        # First level shallow copy.
        return {k: _try_copy(v) for k, v in self._data.iteritems()}
        
        # The fastest but in-accurate version.
        # return dict(self._data)

    def previous_state(self):
        """
        Returns a ``field -> value`` dict of the state of the instance after it
        was created, saved or deleted the previous time.
        """
        if len(self._states) > 1:
            return self._states[1]
        else:
            return self._states[0]

    def old_state(self):
        """
        Returns a ``field -> value`` dict of the state of the instance after
        it was created, saved or deleted the previous previous time. Returns
        the previous state if there is no previous previous state.
        """
        return self._states[0]

    def _changes(self, other, current):
        res = {}
        for key in set(other.keys()) | set(current.keys()):
            was, now = other.get(key), current.get(key)
            if was != now:
                res[key] = (was, now)
        return res

    def changes(self):
        """
        Returns a ``field -> (previous value, current value)`` dict of changes
        from the previous state to the current state.
        """
        return self._changes(self.previous_state(), self.current_state())

    def old_changes(self):
        """
        Returns a ``field -> (previous value, current value)`` dict of changes
        from the old state to the current state.
        """
        return self._changes(self.old_state(), self.current_state())

    def previous_changes(self):
        """
        Returns a ``field -> (previous value, current value)`` dict of changes
        from the old state to the previous state.
        """
        return self._changes(self.old_state(), self.previous_state())

    def was_persisted(self):
        """
        Returns true if the instance was persisted (saved) in its old
        state.

        Examples::

            >>> user = User()
            >>> user.save()
            >>> user.was_persisted()
            False

            >>> user = User.objects.get(pk=1)
            >>> user.delete()
            >>> user.was_persisted()
            True
        """
        pk_name = self._meta.pk.name
        return bool(self.old_state()[pk_name])

    def is_persisted(self):
        """
        Returns true if the instance is persisted (saved) in its current
        state.

        Examples:

            >>> user = User()
            >>> user.save()
            >>> user.is_persisted()
            True

            >>> user = User.objects.get(pk=1)
            >>> user.delete()
            >>> user.is_persisted()
            False
        """
        return bool(self.pk)

    def old_instance(self):
        """
        Returns an instance of this model in its old state.
        """
        return self.__class__(**self.old_state())

    def previous_instance(self):
        """
        Returns an instance of this model in its previous state.
        """
        return self.__class__(**self.previous_state())
        
    def reload(self, *args, **kwargs):
        res = super(ChangesMixin, self).reload(*args, **kwargs)
        self._states = []
        self._save_state(new_instance=True)
        return res


def _post_save(sender, **kwargs):
    kwargs['document']._save_state(new_instance=False, event_type=SAVE)


def _post_delete(sender, **kwargs):
    kwargs['document']._save_state(new_instance=False, event_type=DELETE)
