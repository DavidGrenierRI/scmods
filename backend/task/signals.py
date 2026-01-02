from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from task.models import Task


@receiver(m2m_changed, sender=Task.prerequisites.through)
def validate_prerequisites_on_change(sender, instance, action, **kwargs):
    """Validate prerequisite cycles whenever prerequisites are added or removed."""
    if action in ['post_add']:
        instance._validate_no_prerequisite_cycles()