from rest_framework.viewsets import ModelViewSet
from .models import Meal
from .serializers import UserMealSerializer, AdminMealSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework import viewsets, permissions, status
from .permissions import IsAdminUserType

# class MealTypeViewSet(ModelViewSet):
#     queryset = MealType.objects.all()
#     serializer_class = MealTypeSerializer


# class MealTimeViewSet(ModelViewSet):
#     queryset = MealTime.objects.all()
#     serializer_class = MealTimeSerializer
#     permission_classes = [IsAuthenticated]

#     def perform_create(self, serializer):
#         serializer.save(student=self.request.user)
        
# class MealBillViewSet(ModelViewSet):
#     queryset = MealBill.objects.all()
#     serializer_class = MealBillSerializer
#     permission_classes = [IsAuthenticated]
    
#     def get_queryset(self):
#         if self.request.user.USER_TYPE == 'admin':
#             return MealBill.objects.all()
#         return MealBill.objects.filter(student=self.request.user)
        
#     def perform_create(self, serializer):
#         student = self.request.user
#         meal_times = MealTime.objects.filter(student=student, status=True)
        
#         total_amount = 0
#         for meal_time in meal_times:
#             if meal_time.meal_choice == "full":
#                 total_amount += meal_time.meal_type.full_price
#             elif meal_time.meal_choice in ["half_day", "half_night"]:
#                 total_amount += meal_time.meal_type.half_price
#         serializer.save(student=student, total_amount=total_amount)

# class MealViewSet(viewsets.ModelViewSet):
#     queryset = Meal.objects.all()
#     permission_classes = [permissions.IsAuthenticated,IsAdminUserType]

#     def get_serializer_class(self):
#         if self.request.user.user_type == 'Admin':
#             return AdminMealSerializer
#         return UserMealSerializer

#     def get_queryset(self):
#         if self.request.user.user_type == 'Admin':
#             return Meal.objects.all()
#         return Meal.objects.filter(user=self.request.user)

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)

#     @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
#     def all_meals(self, request):
#         queryset = self.get_queryset()
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)

#     @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAdminUser])
#     def update_status(self, request, pk=None):
#         meal = self.get_object()
#         is_paid = request.data.get('is_paid', None)
#         is_active = request.data.get('is_active', None)

#         if is_paid is not None:
#             meal.is_paid = is_paid
#         if is_active is not None:
#             meal.is_active = is_active
#         meal.save()

#         return Response(
#             {"message": "Meal status updated successfully."},
#             status=status.HTTP_200_OK
#         )


class MealViewSet(viewsets.ModelViewSet):
    queryset = Meal.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdminUserType]

    def get_serializer_class(self):
        if self.request.user.user_type == 'Admin':
            return AdminMealSerializer
        return UserMealSerializer

    def get_queryset(self):
        if self.request.user.user_type == 'Admin':
            return Meal.objects.all()
        return Meal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def all_meals(self, request):
        queryset = Meal.objects.all()
        serializer = AdminMealSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAdminUser])
    def update_status(self, request, pk=None):
        meal = self.get_object()
        is_paid = request.data.get('is_paid', None)
        is_active = request.data.get('is_active', None)

        if is_paid is None and is_active is None:
            return Response(
                {"message": "At least one status field ('is_paid' or 'is_active') must be provided."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if is_paid is not None:
            meal.is_paid = is_paid
        if is_active is not None:
            meal.is_active = is_active
        meal.save()

        return Response(
            {"message": "Meal status updated successfully."},
            status=status.HTTP_200_OK
        )
        