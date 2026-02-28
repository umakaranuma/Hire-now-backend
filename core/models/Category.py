from django.db import models


class Category(models.Model):
    """Worker category (Driver, Plumber, etc.)."""

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name
