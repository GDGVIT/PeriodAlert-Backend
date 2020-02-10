from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from fcm_django.models import FCMDevice

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ChatRoom, Messages, Requests, User
from .serializers import (ChatRoomSerializer, RequestsSerializer,
                          UserLoginSerializer, UserSignupSerializer)


# Signe up a new user View
class UserSignupView(APIView):
    permission_classes = (AllowAny,)

    # Sigup user (create new object)
    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)

        if serializer.is_valid():
            user_data = serializer.data
            User.objects.create_user(
                email=user_data['email'], 
                password=user_data['password'], 
                username=user_data['username'], 
                phone_no=user_data['phone_no'],
                date_of_birth=user_data['date_of_birth'])
            return Response({"message":"User Signed up successfully", "User":user_data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message":"Invalid Data"}, status=status.HTTP_400_BAD_REQUEST)

    # Check if user exists or not
    def get(self, request):
        email = request.query_params.get("email")
        password = request.query_params.get("password")
        print(email + "___" + password)
        user = authenticate(email=email, password=password)
        if not user:
            return Response({"message":"User does not exist"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message":"User Already Exists"}, status=status.HTTP_302_FOUND)

# View for user login
class UserLoginView(APIView):
    permission_classes = (AllowAny,)
    
    def post(self, request):
        req_data = request.data
        user = authenticate(email=req_data['email'], password=req_data['password'])
        if not user:
            return Response({"message":"Invalid Details"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "message":"User Logged In", 
                "User":{
                    "id":user.id,
                    "email":user.email,
                    "username":user.username,
                    "phone_no":user.phone_no,
                    "date_of_birth":user.date_of_birth,
                    "token":token.key
            }})

# Signout new user
class UserLogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        user = request.user
        response = {
            "message":"User logged out", 
            "Details":{
                "id": user.id,
                "email":user.email,
                "username":user.username,
                "phone_no":user.phone_no,
                "date_of_birth":user.date_of_birth
            }}
        request.user.auth_token.delete()
        return Response(response, status=status.HTTP_200_OK)

# Register a new device to backend and store registration_id
class FCMRegisterDeviceView(APIView):
    permission_classes = (IsAuthenticated,)

    # Register a new device (create new object)
    def post(self, request):
        req_data = request.data
        user = request.user
        try:
            device = FCMDevice.objects.get(user=user)
            return Response({"message":"Device already registered for the user"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            device = FCMDevice()
            device.device_id = req_data['device_id']
            device.registration_id = req_data['registration_id']
            device.type = "Android"
            device.user = request.user
            device.save()
            return Response(
                {"message":"New Device Registered", 
                "device_details":{
                    "device_id":device.device_id,
                    "registration_id":device.registration_id,
                    "type":device.type,
                    "user":device.user.id
                }},
                status=status.HTTP_201_CREATED)
    
    # Update the device_id or registraton_token for a registered device
    def patch(self, request):
        req_data = request.data
        user = request.user
        try:
            device = FCMDevice.objects.get(user=user)
            if req_data['device_id'] != None:
                device.device_id = req_data['device_id']
            if req_data['registration_id'] != None:
                device.registration_id = req_data['registration_id']
            device.save()
            return Response(
                {"message":"Device registration_id updated",
                "device_details":{
                    "device_id":device.device_id,
                    "registration_id":device.registration_id,
                    "type":device.type,
                    "user":device.user.id
                }}, status=status.HTTP_200_OK)
        except:
            return Response({"message":"User does not have a registered device"}, status=status.HTTP_400_BAD_REQUEST)
            
# Send Alert notification to all the devices other than the users device
class FCMPushNotificationView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        lat = request.query_params.get("lat", None)
        lon = request.query_params.get("lon", None)
        try:
            # Checking if the user making quesry has a registered device
            user = request.user
            try:
                device = FCMDevice.objects.get(user=user)
            except:
                return Response({"message":"The User's device is not registered"}, status=status.HTTP_400_BAD_REQUEST)
            # To get all devices other than the one who made request
            devices = FCMDevice.objects.exclude(user=user)
            devices.send_message(data={"lat":lat, "lon":lon, "user_id":user.id})
           
           # Creating a new request for help in the database
            req_ser = RequestsSerializer(data={
                "user_id":user.id,
                "latitude":lat,
                "longitude":lon
            })
            if req_ser.is_valid():
                req_ser.save()
                return Response({"message":"Sent notificaion", "Request":req_ser.data}, status=status.HTTP_200_OK)
            else:
                return Response({"message":req_ser.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message":str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ViewRequests(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        today_date = datetime.today().strftime('%Y-%m-%d')
        req_objects = Requests.objects.filter(Q(date_time_creation__date=today_date) & ~Q(user_id=user.id))
        response = RequestsSerializer(req_objects, many=True)
        return Response({"message":"Received Requests", "Requests":response.data}, status=status.HTTP_200_OK)
