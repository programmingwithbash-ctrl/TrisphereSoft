from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
  AttendaceViewSet, CatalogViewSet, CirculationViewSet, 
  AcquisitionViewSet, DutyViewSet, MessageViewSet,
  PermissionView, GroupViewSet,
  PublicUserListViewSet, CustomUserViewSet
)

router = DefaultRouter()
router.register(r'attendace', AttendaceViewSet, basename='attendace')
router.register(r'catalog', CatalogViewSet, basename='catalog')
router.register(r'circulation', CirculationViewSet, basename='circulation')
router.register(r'acquisition', AcquisitionViewSet, basename='acquisition')
router.register(r'duty', DutyViewSet, basename='duty')
router.register(r'messages', MessageViewSet)
router.register(r'permissions', PermissionView, basename='permission-list')
router.register(r'groups', GroupViewSet, basename='group')
router.register(r'public-users', PublicUserListViewSet, basename='public-user-list')
router.register(r'users', CustomUserViewSet, basename='custom-user')

urlpatterns = router.urls