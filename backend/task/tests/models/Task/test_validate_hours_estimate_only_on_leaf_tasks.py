from django.core.exceptions import ValidationError
from django.test import TestCase
from client.models import Client
from project.models import Project
from task.models import Task



class ValidateHoursEstimateOnlyOnLeafTasksCases(TestCase):
    @classmethod
    def setUpTestData(cls):
        client = Client.objects.create()
        project = client.projects.create()
        cls.parent_task = project.tasks.create()
        cls.child_task = project.tasks.create(parent=cls.parent_task)
        return super().setUpTestData()

    def test_parent_task_with_hours_estimate(self):
        """Should raise ValidationError."""
        self.parent_task.hours_estimate = 1
        with self.assertRaises(ValidationError):
            self.parent_task._validate_hours_estimate_only_on_leaf_tasks()

    def test_parent_task_without_hours_estimate(self):
        """Should not raise an error."""
        self.parent_task.hours_estimate = 0
        self.parent_task._validate_hours_estimate_only_on_leaf_tasks()

    def test_leaf_node_with_hours_estimate(self):
        """Should not raise an error."""
        # confirm child is leaf node (has no children)
        self.assertFalse(self.child_task.children.exists())
        self.child_task.hours_estimate = 1
        self.child_task._validate_hours_estimate_only_on_leaf_tasks()

    def test_leaf_node_without_hours_estimate(self):
        """
        Should not raise an error. Parent nodes cannot have an hours estimate, but
        leaf nodes are not REQUIRED to have one.
        """
        # confirm child is leaf node (has no children)
        self.assertFalse(self.child_task.children.exists())
        self.child_task.hours_estimate = 0
        self.child_task._validate_hours_estimate_only_on_leaf_tasks()
