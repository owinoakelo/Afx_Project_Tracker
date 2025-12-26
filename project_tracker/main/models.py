import uuid
from django.db import models
from users.models import User

# Create your models here.
class Common(models.Model):
    uid=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Category(Common):
    category_name = models.CharField(max_length=100, blank=False, null=False)
    objective_weight = models.DecimalField(max_digits=3, decimal_places=1, blank=False, null=False)
    scorecard_year = models.IntegerField(blank=False, null=False)

    def __str__(self):
        return self.category_name
    
class Status(Common):
    status_name = models.CharField(max_length=50, choices= [('Planned', 'Planned'), ('On Track', 'On Track'), ('Completed', 'Completed'), ('At Risk', 'At Risk'), ('Delayed', 'Delayed')], default='Not Started', blank=False, null=False)
    date = models.DateField(blank=False, null=False)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.status_name

class Project(Common):
    project_name = models.CharField(max_length=100, blank=False, null=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    measure_initiative_weight=models.DecimalField(max_digits=3, decimal_places=3, blank=False, null=False)
    project_phase=models.CharField(max_length=50, blank=False, null=False, choices=[('Contracting', 'Contracting'), ('Requirement', 'Requirement'), ('Approval', 'Approval'), ('Design', 'Design'), ('Development', 'Development'), ('Testing', 'Testing'), ('Deployment', 'Deployment'), ('Live', 'Live')], default='Planning')
    project_status=models.ForeignKey(Status, on_delete=models.CASCADE)
    stretch_target_date=models.DateField(blank=False, null=False)
    owner=models.ForeignKey(User, on_delete=models.CASCADE)
