from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
# router.register(r'accounts', views.AccountViewset, basename='account')
router.register(r'users', views.UserViewSet, basename='user')

from .views import (
    CreateComplaintView,
    UserComplaintListView,
    AdminComplaintListView,
    AdminResolveComplaintView
)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', views.UserRegistrationApiView.as_view(), name='register'),
    path('activate/<uid64>/<token>/', views.activateAccount, name='activate'),
    path('login/', views.UserLoginApiView.as_view(), name='login'),
    path('logout/', views.UserLogoutApiView.as_view(), name='logout'),
    # path('profile/update/',views.UserProfileUpdateView.as_view(), name='profile-update'),
    # path('change-password/',views.ChangePasswordView.as_view(), name='change-password'),
    # path('user-count/', views.TotalUsersCountView.as_view(), name='user_count'),
    
    path('complaints/create/', CreateComplaintView.as_view(), name='create_complaint'),
    path('complaints/user/', UserComplaintListView.as_view(), name='user_complaint_list'),

    path('complaints/admin/', AdminComplaintListView.as_view(), name='admin_complaint_list'),
    path('complaints/admin/resolve/<int:complaint_id>/', AdminResolveComplaintView.as_view(), name='admin_resolve_complaint'),
]