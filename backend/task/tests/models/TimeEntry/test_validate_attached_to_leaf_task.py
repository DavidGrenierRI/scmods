from django.core.exceptions import ValidationError
from django.test import TestCase
from client.models import Client
from project.models import Project
from task.models import Task, TimeEntry


class ValidateHoursEstimateOnlyOnLeafTasksCases(TestCase):
    @classmethod
    def setUpTestData(cls):
        client = Client.objects.create()
        project = client.projects.create()
        cls.parent_task = project.tasks.create()
        cls.leaf_task = project.tasks.create(parent=cls.parent_task)
        return super().setUpTestData()

    def test_parent_task(self):
        """Should raise ValidationError."""
        time_entry = self.parent_task.time_entries.create(skip_validation=True)
        with self.assertRaises(ValidationError):
            time_entry._validate_attached_to_leaf_task()

    def test_leaf_task(self):
        """Should not raise ValidationError."""
        time_entry = self.leaf_task.time_entries.create(skip_validation=True)
        time_entry._validate_attached_to_leaf_task()
