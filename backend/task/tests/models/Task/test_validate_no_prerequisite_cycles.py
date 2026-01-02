from django.core.exceptions import ValidationError
from django.test import TestCase
from client.models import Client
from project.models import Project
from task.models import Task


class ValidateNoPrerequisiteCyclesCases(TestCase):
    @classmethod
    def setUpTestData(cls):
        client = Client.objects.create()
        cls.project = client.projects.create()
        return super().setUpTestData()

    def test_root_task(self):
        """Should not raise ValidationError."""
        task1 = self.project.tasks.create()
        task1._validate_no_prerequisite_cycles()

    def test_simple_chain(self):
        """Should not raise ValidationError."""
        task1 = self.project.tasks.create()
        task2 = self.project.tasks.create()
        task2.prerequisites.add(task1)
        task2._validate_no_prerequisite_cycles()

    def test_self_reference(self):
        """Should raise ValidationError."""
        task1 = self.project.tasks.create()
        task1.prerequisites.add(task1)
        with self.assertRaises(ValidationError):
            task1._validate_no_prerequisite_cycles()

    def test_cycle_length_2(self):
        """Should raise ValidationError."""
        task1 = self.project.tasks.create()
        task2 = self.project.tasks.create()
        task1.prerequisites.add(task2)
        task2.prerequisites.add(task1)

        with self.assertRaises(ValidationError):
            task1._validate_no_prerequisite_cycles()

        with self.assertRaises(ValidationError):
            task2._validate_no_prerequisite_cycles()

    def test_cycle_length_3(self):
        """Should raise ValidationError."""
        task1 = self.project.tasks.create()
        task2 = self.project.tasks.create()
        task3 = self.project.tasks.create()
        task1.prerequisites.add(task3)
        task2.prerequisites.add(task1)
        task3.prerequisites.add(task2)

        with self.assertRaises(ValidationError):
            task1._validate_no_prerequisite_cycles()

        with self.assertRaises(ValidationError):
            task2._validate_no_prerequisite_cycles()

        with self.assertRaises(ValidationError):
            task3._validate_no_prerequisite_cycles()

    def test_multiple_paths_no_cycles(self):
        """Should not raise ValidationError."""
        task1 = self.project.tasks.create()
        task2 = self.project.tasks.create()
        task3 = self.project.tasks.create()
        task4 = self.project.tasks.create()
        task5 = self.project.tasks.create()
        task6 = self.project.tasks.create()
        task7 = self.project.tasks.create()

        # Path 1: task1 -> task2 -> task3
        task2.prerequisites.add(task1)
        task3.prerequisites.add(task2)

        # Path 2: task4 -> task5 -> task6
        task5.prerequisites.add(task4)
        task6.prerequisites.add(task5)

        # task7 depends on both paths
        task7.prerequisites.add(task3, task6)

        task7._validate_no_prerequisite_cycles()

    def test_multiple_chains_with_cycles(self):

        """Should not raise ValidationError."""
        task1 = self.project.tasks.create()
        task2 = self.project.tasks.create()
        task3 = self.project.tasks.create()
        task4 = self.project.tasks.create()
        task5 = self.project.tasks.create()
        task6 = self.project.tasks.create()
        task7 = self.project.tasks.create()

        # Path 1: task1 -> task2 -> task3
        task2.prerequisites.add(task1)
        task3.prerequisites.add(task2)

        # Path 2: task4 -> task5 -> task6
        task5.prerequisites.add(task4)
        task6.prerequisites.add(task5)

        # task7 depends on both paths
        task7.prerequisites.add(task3, task6)

        # Add cycle to path 1
        task1.prerequisites.add(task2)

        with self.assertRaises(ValidationError):
            task7._validate_no_prerequisite_cycles()

    def test_diamond_pattern(self):
        """Should not raise ValidationError."""
        task1 = self.project.tasks.create()
        task2 = self.project.tasks.create()
        task3 = self.project.tasks.create()
        task4 = self.project.tasks.create()

        task2.prerequisites.add(task1)
        task3.prerequisites.add(task1)
        task4.prerequisites.add(task2, task3)

        task1._validate_no_prerequisite_cycles()
        task2._validate_no_prerequisite_cycles()
        task3._validate_no_prerequisite_cycles()
        task4._validate_no_prerequisite_cycles()
