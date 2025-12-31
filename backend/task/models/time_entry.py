from django.conf import settings
from django.db import models


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
    )
    start_time = models.DateTimeField(blank=True, null=True, default=None)
    end_time = models.DateTimeField(blank=True, null=True, default=None)
