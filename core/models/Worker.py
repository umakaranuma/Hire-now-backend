from django.db import models
from core.models.User import User
from core.models.Category import Category


class Worker(models.Model):
    """Worker profile linked to a user and category."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    description = models.TextField()
    experience_years = models.IntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_worker"

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.category})"
