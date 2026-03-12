from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from hms_sync.models import Department, Doctor, DoctorTiming
from .serializers import DepartmentSerializer, DoctorSerializer, DoctorTimingSerializer, DoctorProfileSerializer
from .models import DoctorProfile
from accounts.models import DoctorUser

# Create your views here.

class DepartmentListView(APIView):
    """API endpoint to get all departments"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        departments = Department.objects.all()
        serializer = DepartmentSerializer(departments, many=True)
        return Response({
            'departments': serializer.data
        }, status=status.HTTP_200_OK)


class AllDoctorsView(APIView):
    """API endpoint to get all doctors with profile photos"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        doctors = Doctor.objects.all()
        serializer = DoctorSerializer(doctors, many=True, context={'request': request})
        return Response({
            'doctors': serializer.data
        }, status=status.HTTP_200_OK)


class DoctorListByDepartmentView(APIView):
    """API endpoint to get doctors by department code with profile photos"""
    permission_classes = [AllowAny]
    
    def get(self, request, department_code):
        doctors = Doctor.objects.filter(department=department_code)
        serializer = DoctorSerializer(doctors, many=True, context={'request': request})
        return Response({
            'doctors': serializer.data
        }, status=status.HTTP_200_OK)


class DoctorOwnProfileView(APIView):
    """API endpoint for doctors to view/update their own profile (bio only - photo comes from HMS sync)"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            doctor_user = DoctorUser.objects.get(user=request.user)
            doctor = Doctor.objects.get(code=doctor_user.doctor_code)
            serializer = DoctorSerializer(doctor, context={'request': request})
            return Response({
                'doctor': serializer.data
            }, status=status.HTTP_200_OK)
        except (DoctorUser.DoesNotExist, Doctor.DoesNotExist):
            return Response({
                'error': 'Doctor profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request):
        """Allow doctor to update their bio only"""
        try:
            doctor_user = DoctorUser.objects.get(user=request.user)
            doctor = Doctor.objects.get(code=doctor_user.doctor_code)
            
            # Get or create doctor profile
            profile, created = DoctorProfile.objects.get_or_create(doctor=doctor)
            
            # Update bio only
            if 'bio' in request.data:
                profile.bio = request.data.get('bio')
                profile.save()
            
            serializer = DoctorSerializer(doctor, context={'request': request})
            return Response({
                'message': 'Profile updated successfully',
                'doctor': serializer.data
            }, status=status.HTTP_200_OK)
        except (DoctorUser.DoesNotExist, Doctor.DoesNotExist):
            return Response({
                'error': 'Doctor profile not found'
            }, status=status.HTTP_404_NOT_FOUND)


class DoctorTimingView(APIView):
    """API endpoint to get doctor timing by doctor code"""
    permission_classes = [AllowAny]
    
    def get(self, request, doctor_code):
        timings = DoctorTiming.objects.filter(code=doctor_code)
        if not timings.exists():
            return Response({
                'message': 'No timing found for this doctor'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = DoctorTimingSerializer(timings, many=True)
        return Response({
            'timings': serializer.data
        }, status=status.HTTP_200_OK)

