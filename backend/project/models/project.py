from django.db import models
from django.utils.translation import gettext_lazy as _


class Project(models.Model):
    class ProjectStatus(models.TextChoices):
        EVALUATING_RFP = "EVALUATING_RFP", _("Evaluating RFP")
        WRITING_RFP = "WRITING_RFP", _("Writing RFP")
        BOOKED = "BOOKED", _("Booked (unstarted)")
        LOST = "LOST", _("Lost")
        NOT_AWARDED = "NOT_AWARDED", _("Not awarded")
        STARTED = "STARTED", _("Started")
        COMPLETED = "COMPLETED", _("Completed")

    client = models.ForeignKey(
        to="client.Client", related_name="projects", on_delete=models.CASCADE
    )
    type = models.ForeignKey(
        to="project.ProjectType",
        related_name="projects",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    priority = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(
        choices=ProjectStatus, max_length=20, default=ProjectStatus.EVALUATING_RFP
    )

    class Meta:
        ordering = ["client__name", "name"]

    def __str__(self):
        return f"{self.client.name} - {self.name}"
