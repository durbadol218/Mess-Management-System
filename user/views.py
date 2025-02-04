from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets,status
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import User_Model, Complaint
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserSerializer, ComplaintSerializer
from django.shortcuts import redirect
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from rest_framework.permissions import IsAuthenticated
from django.contrib import messages
from rest_framework.pagination import PageNumberPagination
from .permissions import IsAdminUserType

class UserRegistrationApiView(APIView):
    serializer_class = UserRegisterSerializer

    def post(self, request):
        if request.user.is_authenticated:
            return Response({"detail": "You are already logged in. Log out to create a new account."}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save(is_active=False)  # Ensure the user is inactive by default
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            confirm_link = request.build_absolute_uri(reverse('activate', kwargs={'uid64': uid, 'token': token}))

            try:
                email_subject = "Confirmation Email for Account Activation"
                email_body = render_to_string('confirm_email.html', {'confirm_link': confirm_link})
                email = EmailMultiAlternatives(email_subject, '', to=[user.email])
                email.attach_alternative(email_body, 'text/html')
                email.send()
            except Exception as e:
                user.delete()  # Rollback user creation if email fails
                return Response({"detail": "Failed to send confirmation email. Try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({"detail": "Check your email for confirmation."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class UserRegistrationApiView(APIView):
#     serializer_class = UserRegisterSerializer

#     def post(self, request):
#         if request.user.is_authenticated:
#             return Response({"detail": "You are already logged in. Log out to create a new account."}, status=status.HTTP_400_BAD_REQUEST)
        
#         serializer = self.serializer_class(data=request.data)
#         if serializer.is_valid():
#             user = serializer.save(is_active=False)  
#             token, created = Token.objects.get_or_create(user=user)

#             uid = urlsafe_base64_encode(force_bytes(user.pk))
#             confirm_link = request.build_absolute_uri(reverse('activate', kwargs={'uid64': uid, 'token': token.key}))

#             try:
#                 email_subject = "Confirmation Email for Account Activation"
#                 email_body = render_to_string('confirm_email.html', {'confirm_link': confirm_link})
#                 email = EmailMultiAlternatives(email_subject, '', to=[user.email])
#                 email.attach_alternative(email_body, 'text/html')
#                 email.send()
#             except Exception as e:
#                 user.delete()
#                 return Response({"detail": "Failed to send confirmation email. Try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#             return Response({"detail": "Check your email for confirmation."}, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def activateAccount(request, uid64, token):
    try:
        uid = urlsafe_base64_decode(uid64).decode()
        user = User_Model.objects.get(pk=uid)
    except (User_Model.DoesNotExist, ValueError, TypeError):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your account has been successfully activated.")
        return redirect(reverse('login'))  # Use reverse for URL resolution
    else:
        messages.error(request, "The activation link is invalid or has expired.")
        return redirect(reverse('register'))  # Use reverse for URL resolution

# def activateAccount(request, uid64, token):
#     try:
#         uid = urlsafe_base64_decode(uid64).decode()
#         user = get_user_model().objects.get(pk=uid)
#         if default_token_generator.check_token(user, token):
#             user.is_active = True
#             user.save()
#             return Response({"detail": "Your account has been activated."}, status=status.HTTP_200_OK)
#         else:
#             return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
#     except Exception as e:
#         return Response({"detail": "Invalid request."}, status=status.HTTP_400_BAD_REQUEST)



class UserLoginApiView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            user = authenticate(username=username, password=password)
            if user:
                if not user.is_active:
                    return Response({'error': 'Your account is not active. Check your email for the activation link.'}, status=status.HTTP_403_FORBIDDEN)
                
                token, created = Token.objects.get_or_create(user=user)
                login(request, user)
                return Response({
                    'token': token.key,
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLogoutApiView(APIView):
    def post(self, request):
        try:
            request.user.auth_token.delete()
            logout(request)
            return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        except AttributeError:
            return Response({"error": "You are not logged in."}, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User_Model.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [IsAuthenticated]
    



class ComplaintPagination(PageNumberPagination):
    page_size = 10  # Adjust based on your requirement

class CreateComplaintView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        data['user'] = request.user.id

        serializer = ComplaintSerializer(data=data)
        if serializer.is_valid():
            complaint = serializer.save()
            
            subject = "New Complaint Submitted"
            message = f"Dear {request.user.username},\n\nYour complaint has been successfully submitted. Complaint ID: {complaint.id}.\n\nThank you!"
            
            # Send email to user
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
                fail_silently=False,
            )
            
            # Notify admin about the complaint
            admin_users = User_Model.objects.filter(user_type="Admin")
            admin_emails = [admin.email for admin in admin_users if admin.email]

            if admin_emails:
                admin_message = f"A new complaint has been submitted by {request.user.username}. Complaint ID: {complaint.id}."
                send_mail(
                    "New Complaint Notification",
                    admin_message,
                    settings.DEFAULT_FROM_EMAIL,
                    admin_emails,
                    fail_silently=False,
                )
            return Response({"message": "Complaint created successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserComplaintListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        complaints = Complaint.objects.filter(user=request.user).order_by('-created_at')
        paginator = ComplaintPagination()
        paginated_complaints = paginator.paginate_queryset(complaints, request)
        serializer = ComplaintSerializer(paginated_complaints, many=True)
        return paginator.get_paginated_response(serializer.data)


class AdminComplaintListView(APIView):
    permission_classes = [IsAdminUserType]

    def get(self, request):
        complaints = Complaint.objects.all().order_by('-created_at')
        serializer = ComplaintSerializer(complaints, many=True)
        return Response(serializer.data)

class AdminResolveComplaintView(APIView):
    permission_classes = [IsAdminUserType]

    def post(self, request, complaint_id):
        try:
            complaint = Complaint.objects.get(id=complaint_id)
            complaint.status = 'resolved'
            complaint.save()
            return Response({"message": "Complaint marked as resolved."}, status=status.HTTP_200_OK)
        except Complaint.DoesNotExist:
            return Response({"error": "Complaint not found."}, status=status.HTTP_404_NOT_FOUND)
        
    