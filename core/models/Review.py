from django.db import models
from core.models.User import User
from core.models.Worker import Worker


class Review(models.Model):
    """Rating and review for a worker."""

    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name="reviews")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_review"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.rating} by {self.author} for {self.worker}"
