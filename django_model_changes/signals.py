from django.dispatch import Signal


post_change = Signal()
"""
Signal sent whenever an instance is saved or deleted
and changes have been recorded.
"""
