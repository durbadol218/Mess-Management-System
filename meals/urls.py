from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import MealViewSet, create_bazar_schedule, view_bazar_schedule
router = DefaultRouter()
router.register(r'meals', MealViewSet, basename='meal')

urlpatterns = [
    path('bazar-schedule/create/', create_bazar_schedule, name='create-bazar-schedule'),
    path('bazar-schedule/view/', view_bazar_schedule, name='view-bazar-schedule'),
]

urlpatterns += router.urls
