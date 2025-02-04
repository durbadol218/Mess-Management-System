from rest_framework import serializers
from .constants import USER_TYPE
from rest_framework import serializers
from .models import User_Model, Complaint


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_Model
        fields = [
            'id', 'username', 'full_name', 'email', 'reg_no', 
            'education_details', 'contact_number', 'user_type', 
            'is_approved', 'created_at', 'updated_at'
        ]
    
class UserRegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User_Model
        fields = [
            'username', 'email', 'full_name', 'password', 'confirm_password',
            'education_details', 'contact_number', 'user_type'
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
            username=validated_data.get('username', validated_data['email']),  # Fallback to email if username is absent
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            education_details=validated_data['education_details'],
            contact_number=validated_data['contact_number'],
            user_type=validated_data['user_type']
        )
        user.set_password(validated_data['password'])
        user.is_active = False
        user.save()
        return user

# class UserRegisterSerializer(serializers.ModelSerializer):
#     confirm_password = serializers.CharField(required=True, write_only=True)

#     class Meta:
#         model = User_Model
#         fields = [
#             'username', 'email', 'full_name', 'password', 'confirm_password', 'education_details', 'contact_number', 'user_type'
#         ]
#         # extra_kwargs = {
#         #     'password': {'write_only': True},
#         # }

#     def validate(self, data):
#         if data['password'] != data['confirm_password']:
#             raise serializers.ValidationError({"error": "Passwords do not match."})
#         if User_Model.objects.filter(email=data['email']).exists():
#             raise serializers.ValidationError({"error": "Email already exists."})
#         if User_Model.objects.filter(username=data['username']).exists():
#             raise serializers.ValidationError({"error": "Username already exists."})
#         return data

#     def create(self, validated_data):
#         validated_data.pop('confirm_password')

#         user = User_Model(
#             username=validated_data['username'],
#             email=validated_data['email'],
#             full_name=validated_data['full_name'],
#             education_details=validated_data['education_details'],
#             contact_number=validated_data['contact_number'],
#             user_type=validated_data['user_type']
#         )
#         user.set_password(validated_data['password'])
#         user.is_active = False
#         user.save()
#         return user
    
# class UserLoginSerializer(serializers.Serializer):
#     username = serializers.CharField(required=True)
#     password = serializers.CharField(required=True)
    
    
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError({"detail": "Invalid email or password."})

        if not user.is_active:
            raise serializers.ValidationError({"detail": "User account is not active."})

        data['user'] = user
        return data
# class UserProfileUpdate(serializers.ModelSerializer):
#     phone = serializers.CharField(source='account.phone', required=True)
#     user_type = serializers.ChoiceField(source='account.user_type', choices=USER_TYPE, required=True)
#     image = serializers.ImageField(source='account.image', required=False)
#     new_password = serializers.CharField(required=False, write_only=True)
#     confirm_password = serializers.CharField(required=False, write_only=True)

#     class Meta:
#         model = User
#         fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'user_type', 'image', 'new_password', 'confirm_password']

#     def update(self, instance, validated_data):
#         account_data = validated_data.pop('account', {})
#         instance.username = validated_data.get('username', instance.username)
#         instance.first_name = validated_data.get('first_name', instance.first_name)
#         instance.last_name = validated_data.get('last_name', instance.last_name)
#         instance.email = validated_data.get('email', instance.email)
        
#         new_password = validated_data.get('new_password')
#         confirm_password = validated_data.get('confirm_password')
#         if new_password and new_password == confirm_password:
#             instance.set_password(new_password)

#         instance.save()
        
#         account = instance.account
#         account.phone = account_data.get('phone', account.phone)
#         account.user_type = account_data.get('user_type', account.user_type)
#         account.image = account_data.get('image', account.image)
#         account.save()

#         return instance

class ChangePassword(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)
    
    def validate(self,attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("New password and confirm password do not match.")
        return attrs
    
    def update_password(self,user,validated_data):
        user.set_password(validated_data['new_password'])
        user.save()
        return user
    

class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ['id', 'user', 'category', 'description', 'status', 'created_at','active_complaint']
        read_only_fields = ['user', 'created_at']
    


# class UserProfileUpdate(serializers.Serializer):
#     phone = serializers.CharField(source='account.phone', required=True)
#     user_type = serializers.ChoiceField(source='account.user_type', choices=USER_TYPE, required=True)
#     image = serializers.ImageField(source='account.image', required=False)
    
#     class Meta:
#         model = User
#         fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'user_type', 'image']
    
#     def update(self,instance,validated_data):
#         account_data = validated_data.pop('account',{})
#         instance.username = validated_data.get('username', instance.username)
#         instance.first_name = validated_data.get('first_name', instance.first_name)
#         instance.last_name = validated_data.get('last_name', instance.last_name)
#         instance.email = validated_data.get('email', instance.email)
#         instance.save()
        
#         account = instance.account
#         account.phone = account_data.get('phone', account.phone)
#         account.user_type = account_data.get('user_type', account.user_type)
#         account.image = account_data.get('image', account.image)
#         account.save()

#         return instance
    
    