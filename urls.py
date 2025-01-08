from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OnboardingViewSet

router = DefaultRouter()
router.register(r'onboarding', OnboardingViewSet, basename='onboarding')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/auth/', include('rest_framework.urls')),
]
