from rest_framework import serializers
from .constants import USER_TYPE
from rest_framework import serializers
from .models import User_Model, Complaint, Bill
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_Model
        fields = [
            'id', 'username', 'first_name','last_name', 'email', 'reg_no', 
            'education_details', 'contact_number', 'user_type', 'joined_date','address','profile_image',
            'is_approved', 'created_at', 'updated_at', 'seat_type', 'seat_rent'
        ]
    
class UserRegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(required=True, write_only=True)
    user_type = serializers.ChoiceField(choices=USER_TYPE, required=True)
    seat_type = serializers.ChoiceField(choices=User_Model.SEAT_CHOICES, required=True)
    profile_image = serializers.ImageField(required=False, allow_null=True)
    class Meta:
        model = User_Model
        fields = [
            'username', 'email', 'first_name','last_name', 'password', 'confirm_password',
            'education_details', 'contact_number', 'user_type','seat_type', 'address', 'profile_image', 'joined_date'
        ]

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})

        if User_Model.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "Email is already registered."})

        if 'username' in data and User_Model.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({"username": "Username is already taken."})

        if User_Model.objects.filter(contact_number=data['contact_number']).exists():
            raise serializers.ValidationError({"contact_number": "Contact number is already registered."})

        valid_user_types = [choice[0] for choice in USER_TYPE]
        if data['user_type'] not in valid_user_types:
            raise serializers.ValidationError({"user_type": "Invalid user type."})

        return data
    

    def create(self, validated_data):
        validated_data.pop('confirm_password')

        user = User_Model(
            username=validated_data.get('username', validated_data['email']),
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            education_details=validated_data['education_details'],
            contact_number=validated_data['contact_number'],
            user_type=validated_data['user_type'],
            address=validated_data['address'],
            seat_type=validated_data.get('seat_type', 'double_bed'),
            profile_image=validated_data.get('profile_image'),
            joined_date=validated_data.get('joined_date'))
        user.set_password(validated_data['password'])
        user.is_active = False
        user.save()

        return user
    
    
# class UserRegisterSerializer(serializers.ModelSerializer):
#     confirm_password = serializers.CharField(required=False, write_only=True)
#     user_type = serializers.ChoiceField(choices=USER_TYPE, required=True)
#     profile_image = serializers.ImageField(required=False, allow_null=True)

#     class Meta:
#         model = User_Model
#         fields = [
#             'username', 'email', 'first_name', 'last_name', 'password', 'confirm_password',
#             'education_details', 'contact_number', 'user_type', 'address', 'profile_image', 'joined_date'
#         ]

#     def validate(self, data):
#         request = self.context.get('request')

#         if request and request.user.is_authenticated and request.user.user_type == "Admin":
#             data.pop('password', None)
#             data.pop('confirm_password', None)
#         else:
#             password = data.get('password')
#             confirm_password = data.get('confirm_password')

#             if not password or not confirm_password:
#                 raise serializers.ValidationError({"password": "Password and confirm password are required."})

#             if password != confirm_password:
#                 raise serializers.ValidationError({"password": "Passwords do not match."})

#         return data

#     def create(self, validated_data):
#         request = self.context.get('request')

#         if request and request.user.is_authenticated and request.user.user_type == "Admin":
#             default_password = "Default@123"
#             print("Creating user with default password...")  # Debugging

#             user = User_Model(
#                 username=validated_data.get('username', validated_data['email']),
#                 email=validated_data['email'],
#                 first_name=validated_data['first_name'],
#                 last_name=validated_data['last_name'],
#                 education_details=validated_data['education_details'],
#                 contact_number=validated_data['contact_number'],
#                 user_type=validated_data['user_type'],
#                 address=validated_data['address'],
#                 profile_image=validated_data.get('profile_image'),
#                 joined_date=validated_data.get('joined_date')
#             )

#             user.set_password(default_password)
#             user.is_active = True
#             user.save()

#             print(f"User {user.username} created successfully.")
#             print(f"Stored password hash: {user.password}")
#             print(f"Check password (Default@123): {user.check_password('Default@123')}")

#         else:
#             validated_data.pop('confirm_password', None)
#             user = User_Model(**validated_data)
#             user.set_password(validated_data['password'])
#             user.is_active = False
#             user.save()

#         return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError({"detail": "Invalid username or password."})

        if not user.is_active:
            raise serializers.ValidationError({"detail": "User account is not active."})
        data['user'] = user
        return data



class UserProfileUpdateSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User_Model
        fields = [
            'username', 'email', 'first_name', 'last_name', 'education_details',
            'contact_number', 'address', 'profile_image'
        ]
        extra_kwargs = {
            'email': {'read_only': True},
            'username': {'read_only': True},
        }

    def validate_contact_number(self, value):
        if value:
            user = self.instance
            if User_Model.objects.exclude(id=user.id).filter(contact_number=value).exists():
                raise serializers.ValidationError("This contact number is already registered.")
        return value

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance



class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        user = self.context['request'].user

        if not check_password(attrs['old_password'], user.password):
            raise serializers.ValidationError({"old_password": "Old password is incorrect."})
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "New password and confirm password do not match."})
        return attrs

    def update_password(self, user, validated_data):
        user.set_password(validated_data['new_password'])
        user.save()
        return user

class ComplaintSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    class Meta:
        model = Complaint
        fields = ['id', 'user', 'category', 'description', 'status', 'created_at', 'resolved_at', 'admin_reply', 'active_complaint']
        read_only_fields = ['user', 'created_at','resolved_at','admin_reply']
    
    def get_user(self, obj):
        return obj.user.username if obj.user else "N/A"
    
class BillSerializer(serializers.ModelSerializer):
    meal_bill = serializers.SerializerMethodField()
    
    class Meta:
        model = Bill
        fields = ['user','bill_type','total_amount','due_data','transaction_id','status','meal_bill']
    
    def get_meal_bill(self,obj):
        request = self.context.get('request')
        if request:
            year = request.query_params.get('year')
            month = request.query_params.get('month')
            if year and month:
                return Bill.calculate_meal_bill(obj.user,int(year),int(month))
        return 0
    
