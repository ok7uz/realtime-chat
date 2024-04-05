import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from apps.chat.models import Conversation, Message
from apps.chat.serializers import MessageSerializer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_name}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)


    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        conversation = await database_sync_to_async(Conversation.objects.get)(id=int(self.room_name))
        sender = self.scope["user"]
        
        _message = await database_sync_to_async(Message.objects.create)(
            sender=sender,
            text=message,
            conversation=conversation,
        )
        chat_type = {"type": "chat_message"}
        message_serializer = await sync_to_async(dict)(MessageSerializer(instance=_message).data)
        return_dict = {**chat_type, **message_serializer}
        await self.channel_layer.group_send(self.room_group_name, return_dict) 

    async def chat_message(self, event):
        message = event["text"]
        await self.send(text_data=json.dumps(
            {
                "message": message,
                "sender": event["sender"],
                "timestamp": event["timestamp"],
            }
        ))