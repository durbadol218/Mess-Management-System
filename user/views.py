from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets,status
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import User_Model, Complaint
from .serializers import UserRegisterSerializer, UserLoginSerializer,UserProfileUpdateSerializer, ChangePasswordSerializer, UserSerializer, ComplaintSerializer
from django.shortcuts import redirect
# from rest_framework.authtoken.models import Token
from .models import CustomToken
from rest_framework import permissions
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from rest_framework.permissions import IsAuthenticated
from django.contrib import messages
from rest_framework.pagination import PageNumberPagination
from .permissions import IsAdminUserType
from .models import Bill
from .serializers import BillSerializer
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import datetime
from rest_framework.decorators import action
from rest_framework.response import Response

class UserRegistrationApiView(APIView):
    serializer_class = UserRegisterSerializer

    def post(self, request):
        if request.user.is_authenticated:
            return Response({"detail": "You are already logged in. Log out to create a new account."}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save(is_active=False)
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
                user.delete()
                return Response({"detail": "Failed to send confirmation email. Try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({"detail": "Check your email for confirmation."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        return redirect('https://mess-management-frontend-five.vercel.app/login.html')
    else:
        messages.error(request, "The activation link is invalid or has expired.")
        return redirect('https://mess-management-frontend-five.vercel.app/register.html')



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

                token, created = CustomToken.objects.get_or_create(user=user)
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
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        if not user or not user.is_authenticated:
            return Response({"error": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
        CustomToken.objects.filter(user=user).delete()
        logout(request)
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User_Model.objects.all()
    serializer_class = UserSerializer
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUserType])
    def approve(self, request, pk=None):
        try:
            user = self.get_object()
            user.is_approved = True
            user.is_active = True
            user.save()
            return Response({"message": "User approved successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class UserProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = UserProfileUpdateSerializer(user)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully"}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            serializer.update_password(user, serializer.validated_data)
            return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ComplaintPagination(PageNumberPagination):
    page_size = 10

class CreateComplaintView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        serializer = ComplaintSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            complaint = serializer.save(user=request.user)
            subject = "New Complaint Submitted"
            message = f"Dear {request.user.username},\n\nYour complaint has been successfully submitted. Complaint ID: {complaint.id}.\n\nThank you!"
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
                fail_silently=False,
            )
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
    permission_classes = [IsAuthenticated,IsAdminUserType]
    def get(self, request):
        status_filter = request.GET.get('status', None)
        complaints = Complaint.objects.all().order_by('-created_at')
        if status_filter in ['pending', 'resolved']:
            complaints = complaints.filter(status=status_filter)
        paginator = ComplaintPagination()
        paginated_complaints = paginator.paginate_queryset(complaints, request)
        serializer = ComplaintSerializer(paginated_complaints, many=True)
        return paginator.get_paginated_response(serializer.data)

class AdminResolveComplaintView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserType]
    def post(self, request, complaint_id):
        complaint = get_object_or_404(Complaint, id=complaint_id)
        if complaint.status == 'resolved':
            return Response({"message": "Complaint is already resolved."}, status=status.HTTP_400_BAD_REQUEST)
        reply_message = request.data.get('admin_reply', '').strip()
        if not reply_message:
            return Response({"error": "Admin reply is required to resolve the complaint."}, status=status.HTTP_400_BAD_REQUEST)
        complaint.status = Complaint.STATUS_RESOLVED
        complaint.admin_reply = reply_message
        complaint.save()
        subject = "Complaint Resolved with Reply"
        message = f"Dear {complaint.user.username},\n\nYour complaint (ID: {complaint.id}) has been resolved.\nAdmin Reply: {reply_message}\n\nThank you!"
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [complaint.user.email],
            fail_silently=False,
        )
        return Response({"message": "Complaint marked as resolved with admin reply."}, status=status.HTTP_200_OK)

# class BillViewSet(viewsets.ModelViewSet):
#     serializer_class = BillSerializer
#     permission_classes = [IsAuthenticated]
    
#     def get_queryset(self):
#         user = self.request.user
#         return Bill.objects.filter(user=user)
    
#     @action(detail=False, methods=['get'], url_path='summary/(?P<year>\d+)/(?P<month>\d+)')
#     def bill_summary(self, request, year, month):
#         user = request.user
#         bill = Bill.objects.filter(user=user, due_date__year=year, due_date__month=month).first()
        
#         fixed_bill_summary = {bill_type: amount for bill_type, amount in Bill.FIXED_BILL_AMOUNTS.items()}
#         meal_bill = Bill.calculate_meal_bill(user, int(year), int(month))
#         total_bill = sum(fixed_bill_summary.values()) + meal_bill['total']
        
#         response_data = {
#             "bill_id": bill.id if bill else None,
#             "fixed_bills": fixed_bill_summary,
#             "meal_bills": meal_bill,
#             "total_bill": total_bill
#         }
#         return Response(response_data)


class BillViewSet(viewsets.ModelViewSet):
    serializer_class = BillSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.user_type == 'admin':
            return Bill.objects.all()
        return Bill.objects.filter(user=user)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        
        if year and month:
            queryset = queryset.filter(due_date__year=year, due_date__month=month)
        
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    # @action(detail=False, methods=['get'], url_path='summary/(?P<year>\d{4})/(?P<month>\d{1,2})')
    # def bill_summary(self, request, year, month):
    #     user = request.user
    #     year = int(year)
    #     month = int(month)
        
    #     # Get or compute the bill
    #     bill = Bill.objects.filter(user=user, due_date__year=year, due_date__month=month).first()
        
    #     # Fixed bills: use actual seat_rent + other fixed amounts
    #     fixed_bill_summary = {
    #         'seat_rent': float(user.seat_rent),
    #         'water': float(Bill.FIXED_BILL_AMOUNTS['water']),
    #         'khala': float(Bill.FIXED_BILL_AMOUNTS['khala']),
    #         'net': float(Bill.FIXED_BILL_AMOUNTS['net']),
    #         'current': float(Bill.FIXED_BILL_AMOUNTS['current']),
    #         'other': float(Bill.FIXED_BILL_AMOUNTS['other']),
    #     }

    #     # Calculate meal bill
    #     meal_bill_data = Bill.calculate_meal_bill(user, year, month)
    #     total_meal = float(meal_bill_data['total'])

    #     # Compute total
    #     total_fixed = sum(fixed_bill_summary.values())
    #     total_bill = total_fixed + total_meal

    #     response_data = {
    #         "bill_id": bill.id if bill else None,
    #         "fixed_bills": fixed_bill_summary,
    #         "meal_bills": meal_bill_data,
    #         "total_bill": round(total_bill, 2),
    #     }

    #     return Response(response_data)
    
    #final
    @action(detail=False, methods=['get'], url_path='summary/(?P<year>\d{4})/(?P<month>\d{1,2})')
    def bill_summary(self, request, year, month):
        user = request.user
        year = int(year)
        month = int(month)
        
        bill = Bill.objects.filter(
            user=user, 
            due_date__year=year, 
            due_date__month=month,
            bill_type='all_fixed'
        ).first()
        
        fixed_bill_summary = {
            'seat_rent': float(user.seat_rent),
            'water': float(Bill.FIXED_BILL_AMOUNTS['water']),
            'khala': float(Bill.FIXED_BILL_AMOUNTS['khala']),
            'net': float(Bill.FIXED_BILL_AMOUNTS['net']),
            'current': float(Bill.FIXED_BILL_AMOUNTS['current']),
            'other': float(Bill.FIXED_BILL_AMOUNTS['other']),
        }

        meal_bill_data = Bill.calculate_meal_bill(user, year, month)
        total_meal = float(meal_bill_data['total'])
        total_fixed = sum(fixed_bill_summary.values())
        total_bill = total_fixed + total_meal

        if not bill:
            bill = Bill.objects.create(
                user=user,
                bill_type='all_fixed',
                due_date=datetime.date(year, month, 1),
                status='Pending'
            )
        response_data = {
            "bill_id": bill.id,
            "fixed_bills": fixed_bill_summary,
            "meal_bills": meal_bill_data,
            "total_bill": round(total_bill, 2),
        }

        return Response(response_data)