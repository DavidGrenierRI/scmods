from django.conf import settings
from django.core.exceptions import ValidationError
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
    name = models.CharField(max_length=255, blank=True)
    description = models.TextField(help_text="Detailed description of task.", blank=True)
    instructions = models.TextField(
        help_text=(
            "Specific instructions for completion of task. If using this field, "
            "consider creating child subtasks."
        ), 
        blank=True
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
    schedule_datetime = models.DateTimeField(null=True, default=None, blank=True)
    auto_schedule = models.BooleanField(default=True)
    due_date = models.DateField(null=True, default=None, blank=True)
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

    def __init__(self, *args, **kwargs):
        self._skip_validation = kwargs.pop('skip_validation', False)
        super().__init__(*args, **kwargs)
        self._cached_parent_id = self.parent_id

    def save(self, *args, **kwargs):
        """Save with validation unless explicitly skipped."""
        if not kwargs.pop('skip_validation', False) and not self._skip_validation:
            self.full_clean()
        super().save(*args, **kwargs)
        self._cached_parent_id = self.parent_id

    # ===============================================================================
    # VALIDATION
    # ===============================================================================
    def clean(self):
        """Run all custom validations."""
        super().clean()
        self._validate_hours_estimate_only_on_leaf_tasks()
        if self.id is None or self._parent_updated():
            self._validate_no_parent_cycles()

    def _parent_updated(self):
        return self._cached_parent_id != self.parent_id

    def _validate_hours_estimate_only_on_leaf_tasks(self):
        if self.hours_estimate > 0 and self.is_parent:
            raise ValidationError(
                "Parent tasks cannot have hour estimates. "
                "Estimates should be on leaf tasks only."
            )

    def _validate_no_parent_cycles(self, nodes_in_path=None):
        if nodes_in_path is None:
            nodes_in_path = []
        if self.parent_id is None:
            return
        if self.parent_id in nodes_in_path:
            raise ValidationError(f"Parent/child cycle found at task node {self.id}")
        if self.id:
            nodes_in_path.append(self.id)
        self.parent._validate_no_parent_cycles(nodes_in_path=nodes_in_path)

    def _validate_no_prerequisite_cycles(self, nodes_in_path=None):
        if self.id is None:
            return
        if nodes_in_path is None:
            nodes_in_path = []
        if not self.prerequisites.exists():
            return
        for prerequisite in self.prerequisites.all():
            if prerequisite.id in nodes_in_path: 
                raise ValidationError(
                    f"Circular dependency found at task node {self.id}"
                )
            nodes_in_path.append(self.id)
            prerequisite._validate_no_prerequisite_cycles(nodes_in_path=nodes_in_path)

    # ===============================================================================
    # PROPERTY METHODS
    # ===============================================================================

    @property
    def is_parent(self):
        return self.children.exists()

    @property
    def is_leaf(self):
        return not self.children.exists()