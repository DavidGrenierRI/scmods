from django.core.exceptions import ValidationError
from django.test import TestCase
from client.models import Client
from project.models import Project
from task.models import Task



class ValidateNoParentCyclesCases(TestCase):
    @classmethod
    def setUpTestData(cls):
        client = Client.objects.create()
        cls.project = client.projects.create()
        return super().setUpTestData()

    def test_root_task(self):
        """Should not raise ValidationError."""
        task1 = self.project.tasks.create()
        task1._validate_no_parent_cycles()

    def test_child_task(self):
        """Should not raise ValidationError."""
        task1 = self.project.tasks.create()
        task2 = self.project.tasks.create(parent=task1)
        task2._validate_no_parent_cycles()

    def test_task_with_sibling(self):
        """Should not raise ValidationError."""
        task1 = self.project.tasks.create()
        task2 = self.project.tasks.create(parent=task1)
        task3 = self.project.tasks.create(parent=task1)
        task2._validate_no_parent_cycles()
        task3._validate_no_parent_cycles()

    def test_self_reference(self):
        """Should raise ValidationError."""
        task1 = self.project.tasks.create()
        task1.parent = task1
        with self.assertRaises(ValidationError):
            task1._validate_no_parent_cycles()

    def test_cycle_length_2(self):
        """Should raise ValidationError."""
        task1 = self.project.tasks.create()
        task2 = self.project.tasks.create(parent=task1)
        task1.parent = task2
        task1.save(skip_validation=True)

        with self.assertRaises(ValidationError):
            task1._validate_no_parent_cycles()

        with self.assertRaises(ValidationError):
            task2._validate_no_parent_cycles()

    def test_cycle_length_3(self):
        """Should raise ValidationError."""
        task1 = self.project.tasks.create()
        task2 = self.project.tasks.create(parent=task1)
        task3 = self.project.tasks.create(parent=task2)
        task1.parent = task3
        task1.save(skip_validation=True)

        with self.assertRaises(ValidationError):
            task1._validate_no_parent_cycles()

        with self.assertRaises(ValidationError):
            task2._validate_no_parent_cycles()

        with self.assertRaises(ValidationError):
            task3._validate_no_parent_cycles()
