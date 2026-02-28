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
from core.controllers.WorkerReviewsController import WorkerReviewsController
from core.controllers.ReviewController import ReviewController, ReviewDetailController
from core.controllers.CategoryController import CategoryController, CategoryDetailController
from core.controllers.AuthController import login, register
from core.controllers.AdminController import (
    AdminPendingWorkersController,
    AdminApproveWorkerController,
    AdminRejectWorkerController,
)
from core.controllers.StatsController import StatsController

urlpatterns = [
    path("users", UserController.as_view(), name="get_users"),
    path("users/<int:user_id>", UserDetailController.as_view(), name="user_detail"),
    path("workers", WorkerController.as_view(), name="get_workers"),
    path("workers/nearby", WorkerNearbyController.as_view(), name="workers_nearby"),
    path("workers/<int:worker_id>/reviews", WorkerReviewsController.as_view(), name="worker_reviews"),
    path("workers/<int:worker_id>", WorkerDetailController.as_view(), name="worker_detail"),
    path("reviews", ReviewController.as_view(), name="get_reviews"),
    path("reviews/<int:review_id>", ReviewDetailController.as_view(), name="review_detail"),
    path("categories", CategoryController.as_view(), name="get_categories"),
    path("categories/<int:category_id>", CategoryDetailController.as_view(), name="category_detail"),
    path("stats", StatsController.as_view(), name="get_stats"),
    path("admin/workers/pending", AdminPendingWorkersController.as_view(), name="admin_workers_pending"),
    path("admin/workers/<int:worker_id>/approve", AdminApproveWorkerController.as_view(), name="admin_worker_approve"),
    path("admin/workers/<int:worker_id>/reject", AdminRejectWorkerController.as_view(), name="admin_worker_reject"),
    path("auth/login", login, name="auth_login"),
    path("auth/register", register, name="auth_register"),
]
