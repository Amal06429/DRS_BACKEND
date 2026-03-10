from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser
from django.contrib.auth import login
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.utils.decorators import method_decorator
from .serializers import AdminLoginSerializer, DoctorLoginSerializer, CreateDoctorUserSerializer, DoctorUserListSerializer
from .models import DoctorUser

# Create your views here.

@method_decorator(csrf_exempt, name='dispatch')
class AdminLoginView(APIView):
    """API endpoint for admin login"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            return Response({
                'message': 'Admin login successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class DoctorLoginView(APIView):
    """API endpoint for doctor login"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = DoctorLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            doctor_code = serializer.validated_data['doctor_code']
            login(request, user)
            return Response({
                'message': 'Doctor login successful',
                'doctor_code': doctor_code,
                'token': 'session-based',  # For compatibility
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class CreateDoctorUserView(APIView):
    """API endpoint for admin to create doctor login credentials"""
    permission_classes = [AllowAny]  # Temporarily for testing - change back to IsAdminUser in production
    
    def post(self, request):
        serializer = CreateDoctorUserSerializer(data=request.data)
        if serializer.is_valid():
            doctor_user = serializer.save()
            return Response({
                'message': 'Doctor login credentials created successfully',
                'data': {
                    'doctor_code': doctor_user.doctor_code,
                    'username': doctor_user.user.username,
                    'email': doctor_user.user.email
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetDoctorCredentialsView(APIView):
    """API endpoint to get all doctor credentials (Admin only)"""
    permission_classes = [AllowAny]  # Temporarily for testing - change back to IsAdminUser in production
    
    def get(self, request):
        doctor_users = DoctorUser.objects.all().order_by('-created_at')
        serializer = DoctorUserListSerializer(doctor_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@method_decorator(ensure_csrf_cookie, name='dispatch')
class GetCSRFTokenView(APIView):
    """API endpoint to get CSRF token cookie"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            'detail': 'CSRF cookie set'
        }, status=status.HTTP_200_OK)

