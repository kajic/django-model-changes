from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.db import models
from django.db.models import signals

from .signals import post_change

if TYPE_CHECKING:
    from django.db.models.options import Options

SAVE = 0
DELETE = 1

# Track which classes have had signals connected
_connected_classes: set[type] = set()


class ChangesMixin:
    r"""
    ChangesMixin keeps track of changes for model instances.

    Use with models.Model: ``class MyModel(ChangesMixin, models.Model)``

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

    _states: list[dict[str, Any]]
    _meta: Options
    pk: Any

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        # Connect signals once per class (on first instantiation)
        cls = self.__class__
        if cls not in _connected_classes:
            _connected_classes.add(cls)
            # cls is guaranteed to be a Model subclass at runtime since ChangesMixin
            # must be used with models.Model
            sender: type[models.Model] = cls  # type: ignore[assignment]
            signals.post_save.connect(
                _post_save,
                sender=sender,
                dispatch_uid=f"django-changes-{cls.__name__}",
            )
            signals.post_delete.connect(
                _post_delete,
                sender=sender,
                dispatch_uid=f"django-changes-{cls.__name__}",
            )

        self._states = []
        self._save_state(new_instance=True)

    def _save_state(self, new_instance: bool = False, event_type: str | int = "save") -> None:
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
            post_change.send(sender=self.__class__, instance=self)

    def current_state(self) -> dict[str, Any]:
        """
        Returns a ``field -> value`` dict of the current state of the instance.
        """
        field_names: set[str] = set()
        for f in self._meta.local_fields:
            field_names.add(f.name)
            field_names.add(f.attname)
        return {field_name: getattr(self, field_name) for field_name in field_names}

    def previous_state(self) -> dict[str, Any]:
        """
        Returns a ``field -> value`` dict of the state of the instance after it
        was created, saved or deleted the previous time.
        """
        if len(self._states) > 1:
            return self._states[1]
        return self._states[0]

    def old_state(self) -> dict[str, Any]:
        """
        Returns a ``field -> value`` dict of the state of the instance after
        it was created, saved or deleted the previous previous time. Returns
        the previous state if there is no previous previous state.
        """
        return self._states[0]

    def _changes(
        self, other: dict[str, Any], current: dict[str, Any]
    ) -> dict[str, tuple[Any, Any]]:
        return {key: (was, current[key]) for key, was in other.items() if was != current[key]}

    def changes(self) -> dict[str, tuple[Any, Any]]:
        """
        Returns a ``field -> (previous value, current value)`` dict of changes
        from the previous state to the current state.
        """
        return self._changes(self.previous_state(), self.current_state())

    def old_changes(self) -> dict[str, tuple[Any, Any]]:
        """
        Returns a ``field -> (previous value, current value)`` dict of changes
        from the old state to the current state.
        """
        return self._changes(self.old_state(), self.current_state())

    def previous_changes(self) -> dict[str, tuple[Any, Any]]:
        """
        Returns a ``field -> (previous value, current value)`` dict of changes
        from the old state to the previous state.
        """
        return self._changes(self.old_state(), self.previous_state())

    def was_persisted(self) -> bool:
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
        pk_field = self._meta.pk
        if pk_field is None:
            return False
        return bool(self.old_state()[pk_field.name])

    def is_persisted(self) -> bool:
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

    def old_instance(self) -> ChangesMixin:
        """
        Returns an instance of this model in its old state.
        """
        return self.__class__(**self.old_state())

    def previous_instance(self) -> ChangesMixin:
        """
        Returns an instance of this model in its previous state.
        """
        return self.__class__(**self.previous_state())


def _post_save(sender: type[models.Model], instance: ChangesMixin, **kwargs: Any) -> None:
    instance._save_state(new_instance=False, event_type=SAVE)


def _post_delete(sender: type[models.Model], instance: ChangesMixin, **kwargs: Any) -> None:
    instance._save_state(new_instance=False, event_type=DELETE)
