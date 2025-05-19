from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Notification
from .serializers import NotificationSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminUserType
from django.contrib.auth import get_user_model
from rest_framework.pagination import PageNumberPagination
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings

User_Model = get_user_model()

# class AdminSendNotificationView(APIView):
#     permission_classes = [IsAdminUserType]
#     def post(self, request):
#         user_id = request.data.get('user_id')
#         notification_type = request.data.get('notification_type')
#         message = request.data.get('message')

#         if not user_id or not notification_type or not message:
#             return Response(
#                 {"error": "user_id, notification_type, and message are required."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         try:
#             user = User_Model.objects.get(id=user_id)
#             notification = Notification.objects.create(
#                 user=user,
#                 notification_type=notification_type,
#                 message=message
#             )
#             return Response(
#                 {"message": "Notification sent successfully."},
#                 status=status.HTTP_201_CREATED
#             )
#         except User.DoesNotExist:
#             return Response(
#                 {"error": "User not found."},
#                 status=status.HTTP_404_NOT_FOUND
#             )

class AdminSendNotificationView(APIView):
    permission_classes = [IsAdminUserType]

    def post(self, request):
        user_id = request.data.get('user_id')
        notification_type = request.data.get('notification_type')
        message = request.data.get('message')

        if not user_id or not notification_type or not message:
            return Response(
                {"error": "user_id, notification_type, and message are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User_Model.objects.get(id=user_id)

            notification = Notification.objects.create(
                user=user,
                notification_type=notification_type,
                message=message
            )

            # Send email notification
            email_subject = f"New Notification - {notification_type}"
            email_body = render_to_string('email_template.html', {
                'user': user,
                'notification_type': notification_type,
                'message': message,
            })
            email = EmailMultiAlternatives(email_subject, '', to=[user.email])
            email.attach_alternative(email_body, 'text/html')
            email.send()

            return Response(
                {"message": "Notification sent successfully, and email sent."},
                status=status.HTTP_201_CREATED
            )
        except User_Model.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )
            
            
class NotificationPagination(PageNumberPagination):
    page_size = 10

class AdminListNotificationsView(APIView):
    permission_classes = [IsAdminUserType]

    def get(self, request):
        notifications = Notification.objects.all()
        paginator = NotificationPagination()
        paginated_notifications = paginator.paginate_queryset(notifications, request)
        serializer = NotificationSerializer(paginated_notifications, many=True)
        return paginator.get_paginated_response(serializer.data)
    
class UserNotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        paginator = NotificationPagination()
        paginated_notifications = paginator.paginate_queryset(notifications, request)
        serializer = NotificationSerializer(paginated_notifications, many=True)
        return paginator.get_paginated_response(serializer.data)

class UserMarkNotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id):
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        if notification.is_read:
            return Response({"message": "This notification is already marked as read."}, status=status.HTTP_200_OK)
        notification.mark_as_read()
        return Response({"message": "Notification marked as read."}, status=status.HTTP_200_OK)

    