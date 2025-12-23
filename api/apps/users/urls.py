from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("me/", views.CurrentUserView.as_view(), name="current-user"),
    path("me/profile/", views.UserProfileView.as_view(), name="current-user-profile"),
    path("<str:username>/", views.UserDetailView.as_view(), name="user-detail"),
]
