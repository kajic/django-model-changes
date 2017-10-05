import copy
from mongoengine import signals
from mongoengine.base.proxy import DocumentProxy

from .signals import post_change

SAVE = 0
DELETE = 1


class ChangesMixin(object):

    def __init__(self, *args, **kwargs):
        super(ChangesMixin, self).__init__(*args, **kwargs)
        self.__class__.register_signals()
        
    @classmethod
    def register_signals(cls):
        if not getattr(cls, 'changes_signal_registered', False):
            setattr(cls, 'changes_signal_registered', True)
            signals.post_save.connect(
                _post_save, sender=cls,
            )
            signals.post_delete.connect(
                _post_delete, sender=cls,
            )

    def _save_state(self, new_instance=False, event_type='save', **kwargs):
        if "Historical" in self.__class__.__name__:
            return
        
        # Pipe the pk on deletes so that a correct snapshot of the current
        # state can be taken.
        if event_type == DELETE:
            self.pk = None

        # Send post_change signal unless this is a new instance
        if not new_instance:
            post_change.send(sender=self.__class__, instance=self, 
                changes=self._calculate_changes(**kwargs), 
                **kwargs)

    def _calculate_changes(self, created=False, _changed_fields=None, _original_values=None, **kwargs):
        if _changed_fields is None:
            _changed_fields = getattr(self, '_changed_fields', [])
        if _original_values is None:
            _original_values = getattr(self, '_original_values', {})
            
        if created:
            _changed_fields = self._data.keys()

        res = {}
        for field in _changed_fields:
            if field not in ["_id"]:
                was = _original_values.get(field, None)
                now = getattr(self, field, None)
                res[field] = (was, now)

        return res
        
    def changes(self):
        return self._calculate_changes()

def _post_save(sender, **kwargs):
    kwargs['document']._save_state(new_instance=False, event_type=SAVE, **kwargs)


def _post_delete(sender, **kwargs):
    kwargs['document']._save_state(new_instance=False, event_type=DELETE, **kwargs)
