import json
from datetime import datetime

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.db.models import Q
from rest_framework.authtoken.models import Token

from app.models import ChatRoom, Messages, Requests, User
from app.serializers import ChatRoomSerializer, MessageSerializer

from fcm_django.models import FCMDevice


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        token = self.scope['url_route']['kwargs']['token']
        is_request_acceptor = self.scope['url_route']['kwargs']['is_request_acceptor']
        receiver_id = self.scope['url_route']['kwargs']['receiver_id']
        try:
            user = Token.objects.get(key=token).user
            receiver = User.objects.get(id=receiver_id)

            self.room_name = "room_id"
            self.room_group_name = 'chat_room_%s' % self.room_name
            print(self.room_group_name)

            # Join room group
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )

            self.accept()
        except Token.DoesNotExist:
            print("Not valid user")
            self.close()  
        
        
    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))