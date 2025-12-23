"""
URL configuration for Bivouac.tv API.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def api_root(request):
    """API root endpoint with available endpoints."""
    return Response(
        {
            "message": "Welcome to Bivouac.tv API",
            "version": "1.0.0",
            "docs": {
                "swagger": "/api/docs/",
                "redoc": "/api/redoc/",
                "schema": "/api/schema/",
            },
            "endpoints": {
                "documentaries": "/api/documentaries/",
                "reviews": "/api/reviews/",
                "submissions": "/api/submissions/",
                "auth": "/api/auth/",
                "users": "/api/users/",
            },
        }
    )


urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # API root
    path("api/", api_root, name="api-root"),
    # App URLs
    path("api/documentaries/", include("apps.documentaries.urls")),
    path("api/reviews/", include("apps.reviews.urls")),
    path("api/submissions/", include("apps.submissions.urls")),
    path("api/users/", include("apps.users.urls")),
    # Authentication
    path("api/auth/", include("dj_rest_auth.urls")),
    path("api/auth/registration/", include("dj_rest_auth.registration.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Debug toolbar
    try:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass
