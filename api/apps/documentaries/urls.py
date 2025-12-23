from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "documentaries"

router = DefaultRouter()
router.register("", views.DocumentaryViewSet, basename="documentary")

urlpatterns = [
    # Taxonomy endpoints
    path("sports/", views.SportListView.as_view(), name="sport-list"),
    path("themes/", views.ThemeListView.as_view(), name="theme-list"),
    path("regions/", views.RegionListView.as_view(), name="region-list"),
    path("platforms/", views.PlatformListView.as_view(), name="platform-list"),
    path("people/", views.PersonListView.as_view(), name="person-list"),
    # Watchlist
    path("watchlist/", views.WatchlistViewSet.as_view({
        "get": "list",
        "post": "create",
    }), name="watchlist-list"),
    path("watchlist/<int:pk>/", views.WatchlistViewSet.as_view({
        "delete": "destroy",
    }), name="watchlist-detail"),
    # Watched list
    path("watched/", views.WatchedViewSet.as_view({
        "get": "list",
        "post": "create",
    }), name="watched-list"),
    path("watched/<int:pk>/", views.WatchedViewSet.as_view({
        "delete": "destroy",
    }), name="watched-detail"),
    # Documentary routes (must be last due to slug matching)
    path("", include(router.urls)),
]
