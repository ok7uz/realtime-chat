import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.exceptions import DenyConnection
from django.shortcuts import get_object_or_404

from apps.chat.models import Conversation, Message
from apps.chat.serializers import MessageSerializer
from apps.user.models import User
from apps.user.serializers import UserSerializer


class ChatConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_name = None
        self.room_group_name = None

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_name}'

        if not self.scope['user'].is_authenticated:
            raise DenyConnection()
    
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        action = text_data_json['action']

        if action == 'message':
            message = text_data_json['message']
            conversation = await database_sync_to_async(get_object_or_404)(Conversation, id=self.room_name)
            sender = self.scope['user']

            _message = await database_sync_to_async(Message.objects.create)(
                sender=sender,
                text=message,
                conversation=conversation,
            )
            chat_type = {'type': 'chat_message'}
            message_data = await sync_to_async(dict)(MessageSerializer(instance=_message).data)
            user = await sync_to_async(get_object_or_404)(User, id=message_data['sender'])
            user_data = await sync_to_async(dict)(UserSerializer(instance=user).data)
            message_data['sender'] = user_data
            return_dict = {**chat_type, **message_data}
            await self.channel_layer.group_send(self.room_group_name, return_dict)
        elif action == 'typing':
            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'chat_action',
                'action': 'typing',
                'sender': self.scope['user'].id
            })

    async def chat_message(self, event):
        message = event['text']
        await self.send(text_data=json.dumps(
            {
                'message': message,
                'sender': event['sender'],
                'timestamp': event['timestamp'],
            }
        ))

    async def chat_action(self, event):
        await self.send(text_data=json.dumps(event))
