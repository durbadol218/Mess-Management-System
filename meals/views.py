from rest_framework.viewsets import ModelViewSet
from .models import Meal
from .serializers import UserMealSerializer, AdminMealSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from rest_framework import viewsets, permissions, status
from .permissions import IsAdminUserType
from rest_framework.decorators import action
from django.db.models import Count
from meals.permissions import IsAdminUserType

from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from .models import BazarSchedule
from .serializers import BazarScheduleSerializer
from django.utils.dateparse import parse_date
from user.models import User_Model
from django.core.mail import send_mail
from django.conf import settings


class MealViewSet(viewsets.ModelViewSet):
    queryset = Meal.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.user.user_type == 'Admin':
            return AdminMealSerializer
        return UserMealSerializer

    def get_queryset(self):
        queryset = Meal.objects.all() if self.request.user.user_type == 'Admin' else Meal.objects.filter(user=self.request.user)
        date_param = self.request.query_params.get("date")
        if date_param:
            parsed_date = parse_date(date_param)
            if parsed_date:
                queryset = queryset.filter(date=parsed_date)
        return queryset
        
    def perform_create(self, serializer):
        if self.request.user.user_type == 'Admin':
            user_id = self.request.data.get('user')
            user = User_Model.objects.get(id=user_id)
            serializer.save(user=user)
        else:
            serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUserType])
    def all_meals(self, request):
        queryset = Meal.objects.all()
        serializer = AdminMealSerializer(queryset, many=True)
        return Response(serializer.data)
        
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        try:
            meal = self.get_object()
            serializer = self.get_serializer(meal, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Meal status updated successfully."}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Meal.DoesNotExist:
            return Response({"error": "Meal not found."}, status=status.HTTP_404_NOT_FOUND)
    
    def destroy(self, request, *args, **kwargs):
        meal = self.get_object()
        if request.user.user_type != 'Admin' and meal.user != request.user:
            return Response({"error": "You are not allowed to delete this meal."}, status=status.HTTP_403_FORBIDDEN)
        meal.delete()
        return Response({"message": "Meal deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
    # @action(detail=False, methods=['get'], url_path='count/(?P<user_id>\d+)/(?P<year>\d+)/(?P<month>\d+)')
    # def meal_count(self, request, user_id, year, month):
    #     meals = Meal.objects.filter(user_id=user_id, date__year=year, date__month=month)
    #     meal_counts = meals.values("meal_choice").annotate(count=Count("meal_choice"))
    #     response_data = {meal["meal_choice"]: meal["count"] for meal in meal_counts}
    #     return Response(response_data)
    
    @action(detail=False, methods=['get'], url_path='count/(?P<year>\d+)/(?P<month>\d+)')
    def meal_count(self, request, year, month):
        user = request.user
        meals = Meal.objects.filter(user=user, date__year=year, date__month=month,is_active=True)
        meal_counts = meals.values("meal_choice").annotate(count=Count("meal_choice"))
        meal_summary = {meal["meal_choice"]: meal["count"] for meal in meal_counts}
        total_bill = sum(Meal.MEAL_PRICES.get(meal_type, 0) * count for meal_type, count in meal_summary.items())
        response_data = {
            "meal_summary": meal_summary,
            "total_bill": total_bill
        }
        return Response(response_data)
    

# class MealCountAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, user_id, year, month):
#         meal_counts = Meal.count_meals_for_user(user_id, year, month)
#         return Response(meal_counts)



@api_view(['POST'])
@permission_classes([IsAdminUserType])
def create_bazar_schedule(request):
    if request.method == 'POST':
        serializer = BazarScheduleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            schedule = serializer.save(user=request.user)
            subject = "Bazar Schedule Assigned"
            message = f"Dear {schedule.user.username},\n\nYou have been assigned a bazar schedule on {schedule.schedule_date}.\n\nThank you!"
            recipient_email = schedule.user.email
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [recipient_email],
                fail_silently=False,
            )
        return Response({"message": "Bazar schedule created and email sent successfully!"}, status=201)
    return Response(serializer.errors, status=400)

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def view_bazar_schedule(request):
#     if request.user.account_type == 'User':
#         schedules = BazarSchedule.objects.filter(user=request.user)
#         serializer = BazarScheduleSerializer(schedules, many=True)
#         return Response(serializer.data)
#     return Response({"detail": "You don't have permission to view this schedule."}, status=403)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_bazar_schedule(request):
    if request.user.user_type == 'Admin':
        schedules = BazarSchedule.objects.all()
    else:
        schedules = BazarSchedule.objects.filter(user=request.user)
    serializer = BazarScheduleSerializer(schedules, many=True)
    return Response(serializer.data)


# @action(detail=True, methods=['patch'], permission_classes=[IsAdminUserType])
# def verify_bazar_schedule(request, schedule_id):
#     try:
#         schedule = BazarSchedule.objects.get(id=schedule_id)
#     except BazarSchedule.DoesNotExist:
#         return Response({"error": "Schedule not found"}, status=404)

#     schedule.is_completed = request.data.get("is_completed", False)
#     schedule.save()

#     if schedule.is_verified:
#         subject = "Bazar Schedule Verified"
#         message = f"Dear {schedule.user.username},\n\nYour bazar schedule on {schedule.schedule_date} has been verified by the admin.\n\nBest regards!"
#         send_mail(
#             subject,
#             message,
#             settings.DEFAULT_FROM_EMAIL,
#             [schedule.user.email],
#             fail_silently=False,
#         )
#     return Response({"message": "Schedule verification updated successfully!"}, status=200)

