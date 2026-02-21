import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken
from .models import Message
from app.message.models import InappropriateMessageReport
# from app.message.views import message_checker
from app.message.ai_helper.content_classifier import message_checker

User = get_user_model()



class MessageConsumer(AsyncWebsocketConsumer):
    """
    A consumer for handling real-time messages between users.
    """
    async def connect(self):
        # Step 1: extract token from headers
        token = None
        for header in self.scope.get("headers", []):
            if header[0] == b"authorization":
                token = header[1].decode().split(" ")[-1]  # Bearer <token>
                break

        if not token:
            await self.close()
            return

        # Step 2: validate JWT and extract payload
        try:
            validated = UntypedToken(token)
            payload = validated.payload
            user_id = payload.get("user_id")
        except InvalidToken:
            await self.close()
            return

        # Step 3: fetch authenticated user
        try:
            self.user = await database_sync_to_async(User.objects.get)(user_id=user_id)
        except User.DoesNotExist:
            await self.close()
            return

        # Step 4: build chat room
        self.receiver_id = self.scope["url_route"]["kwargs"].get("receiver_id")

        if not self.receiver_id:
            await self.close()
            return

        try:
            self.receiver = await database_sync_to_async(User.objects.get)(user_id=self.receiver_id)
        except User.DoesNotExist:
            await self.close()
            return

        # Step 5: build deterministic chat room name
        uid1 = min(self.user.user_id, self.receiver.user_id)
        uid2 = max(self.user.user_id, self.receiver.user_id)
        self.room_group_name = f"chat_{uid1}_{uid2}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        print("User authenticated:", self.user.user_id)
        await self.accept()


    async def disconnect(self, close_code):
        """
        This method is called when the WebSocket closes.
        """
        # Check if room_group_name is set before trying to discard it
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """
        This method is called when we receive a message from WebSocket.
        """
        text_data_json = json.loads(text_data)
        message_content = text_data_json['content']
        message_type = text_data_json.get('message_type', 'text')
        file_url = text_data_json.get('file_url', None)

        # Save the message in the database
        ai_response = message_checker(text_message=message_content)
        print("ai _response",ai_response)
        message = await self.save_message(message_content, message_type, file_url, ai_response)

        # Send the message to the WebSocket group (to both sender and receiver)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message.content,
                'sender': message.sender.full_name,
                'receiver': message.receiver.full_name,
                'message_type': message.message_type,
                'file_url': message.file_url,
                'ai_approval_status': message.ai_approval_status,
            }
        )

    async def chat_message(self, event):
        """
        This method handles broadcasting the message to the WebSocket.
        """
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'receiver': event['receiver'],
            'message_type': event['message_type'],
            'file_url': event['file_url'],
            'ai_approval_status': event['ai_approval_status'],
        }))

    @database_sync_to_async
    def save_message(self, content, message_type, file_url,ai_response):
        """
        Saves a message to the database and returns it.
        """
        # message = Message.objects.create(
        #     sender=self.user,
        #     receiver=self.receiver,
        #     content=content,
        #     message_type=message_type,
        #     file_url=file_url,
        #     ai_approval_status=ai_response
        # )
        message = Message.objects.create(
            sender=self.user,
            receiver=self.receiver,
            message_type=message_type,
            content=content,
            file_url=file_url,
            ai_approval_status=ai_response["ai_approval_status"],
            admin_decision="approved"
        )

        if ai_response["ai_approval_status"] == "inappropriate":
            InappropriateMessageReport.objects.create(
                sender=self.user,
                receiver=self.receiver,
                assigned_job="AI moderation",
                reported_reason=ai_response["reported_reason"],
                reported_title=ai_response["reported_title"],
                message_content=content,
                admin_decision="pending"
            )
        print(message)
        return message