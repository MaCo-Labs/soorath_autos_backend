# Backend/myapp/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VehicleListAPIView,
    VehicleDetailAPIView,
    FeaturedVehicleListView,
    VehicleAdminViewSet,
    DashboardStatsView,
)

router = DefaultRouter()
router.register(r'admin/vehicles', VehicleAdminViewSet, basename='admin-vehicles')

urlpatterns = [
    # ── Public ──────────────────────────────────────────
    path('api/vehicles/',           VehicleListAPIView.as_view(),     name='vehicle-list'),
    path('api/vehicles/<int:pk>/',  VehicleDetailAPIView.as_view(),   name='vehicle-detail'),
    path('api/featured/',           FeaturedVehicleListView.as_view(), name='featured'),

    # ── Admin ────────────────────────────────────────────
    path('api/dashboard/stats/',    DashboardStatsView.as_view(),     name='dashboard-stats'),
    path('api/',                    include(router.urls)),
]