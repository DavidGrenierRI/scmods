from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError


class TimeEntry(models.Model):
    task = models.ForeignKey(
        to="task.Task", related_name="time_entries", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='time_entries',
        help_text="User who performed the work",
        null=True,
        blank=True
    )
    start_time = models.DateTimeField(blank=True, null=True, default=None)
    end_time = models.DateTimeField(blank=True, null=True, default=None)

    def __init__(self, *args, **kwargs):
        self._skip_validation = kwargs.pop('skip_validation', False)
        super().__init__(*args, **kwargs)
        self._cached_task_id = self.task_id

    def save(self, *args, **kwargs):
        """Save with validation unless explicitly skipped."""
        if not kwargs.pop('skip_validation', False) and not self._skip_validation:
            self.full_clean()
        super().save(*args, **kwargs)
        self._cached_task_id = self.task_id

    # ===============================================================================
    # VALIDATION
    # ===============================================================================
    def clean(self):
        """Run all custom validations."""
        super().clean()
        if self.id is None or self._task_updated():
            self._validate_attached_to_leaf_task()

    def _task_updated(self):
        return self._cached_task_id != self.task_id

    def _validate_attached_to_leaf_task(self):
        if self.task.is_parent:
            raise ValidationError(
                "Time entries can only be applied to leaf tasks."
            )
