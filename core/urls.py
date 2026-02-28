"""
API URL routing for core app.
"""
from django.urls import path

from core.controllers.UserController import UserController, UserDetailController
from core.controllers.WorkerController import (
    WorkerController,
    WorkerDetailController,
    WorkerNearbyController,
)
from core.controllers.ReviewController import ReviewController, ReviewDetailController
from core.controllers.CategoryController import CategoryController, CategoryDetailController
from core.controllers.AuthController import LoginView, RegisterView

urlpatterns = [
    path("users/", UserController.as_view()),
    path("users/<int:pk>/", UserDetailController.as_view()),
    path("workers/", WorkerController.as_view()),
    path("workers/nearby/", WorkerNearbyController.as_view()),
    path("workers/<int:pk>/", WorkerDetailController.as_view()),
    path("reviews/", ReviewController.as_view()),
    path("reviews/<int:pk>/", ReviewDetailController.as_view()),
    path("categories/", CategoryController.as_view()),
    path("categories/<int:pk>/", CategoryDetailController.as_view()),
    path("auth/login/", LoginView.as_view()),
    path("auth/register/", RegisterView.as_view()),
]
