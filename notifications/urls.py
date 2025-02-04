# from django.urls import path
# from .views import NotificationListView, MarkNotificationReadView, CreateNotificationView

# urlpatterns = [
#     path('notifications/', NotificationListView.as_view(), name='notification_list'),
#     path('notifications/<int:notification_id>/read/', MarkNotificationReadView.as_view(), name='mark_notification_read'),
#     path('notifications/create/', CreateNotificationView.as_view(), name='create_notification'),
# ]


from django.urls import path
from .views import (
    AdminSendNotificationView,
    AdminListNotificationsView,
    UserNotificationListView,
    UserMarkNotificationReadView,
)

urlpatterns = [
    path('admin/send-notification/', AdminSendNotificationView.as_view(), name='admin_send_notification'),
    path('admin/notifications/', AdminListNotificationsView.as_view(), name='admin_list_notifications'),

    path('user/notifications/', UserNotificationListView.as_view(), name='user_notifications'),
    path('user/notifications/mark-read/<int:notification_id>/', UserMarkNotificationReadView.as_view(), name='mark_notification_read'),
]
