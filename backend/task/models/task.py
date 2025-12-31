from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Task(models.Model):
    class TaskStatus(models.TextChoices):
        NOT_STARTED = "NOT_STARTED", _("Not Started")
        IN_PROCESS = "IN_PROCESS", _("In Process")
        COMPLETED = "COMPLETED", _("Completed")

    project = models.ForeignKey(
        to="project.Project", related_name="tasks", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    description = models.TextField(help_text="Detailed description of task.")
    instructions = models.TextField(
        help_text=(
            "Specific instructions for completion of task. If using this field, "
            "consider creating child subtasks."
        )
    )
    status = models.CharField(
        max_length=20, choices=TaskStatus.choices, default=TaskStatus.NOT_STARTED
    )
    parent = models.ForeignKey(
        to="task.Task",
        related_name="children",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
    )
    prerequisites = models.ManyToManyField(
        to="self", symmetrical=False, related_name="dependents", blank=True
        )
    hours_estimate = models.FloatField(
        default=0, help_text="Estimated hours to complete"
    )
    dependent_hours = models.FloatField(default=0)
    buffer_before = models.PositiveSmallIntegerField(
        default=0,
        help_text="Buffer days between scheduled prerequisites and start of task",
    )
    buffer_after = models.PositiveSmallIntegerField(
        default=0,
        help_text=(
            "Buffer days between completion of task and scheduling of dependencies"
        ),
    )
    schedule_datetime = models.DateTimeField(null=True, default=None)
    auto_schedule = models.BooleanField(default=True)
    due_date = models.DateField(null=True, default=None)
    risk_hours = models.FloatField(
        default=0, 
        help_text="Number of hours estimated over due date for task to be completed."
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        help_text="User assigned to complete this task"
    )
    auto_assign = models.BooleanField(
        default=True,
        help_text="Whether scheduler should automatically assign this task"
    )


