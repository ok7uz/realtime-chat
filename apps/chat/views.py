from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from apps.chat.models import Conversation
from apps.chat.serializers import ConversationListSerializer, ConversationSerializer
from apps.user.models import User


class ConversationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        conversation_list = Conversation.objects.filter(
            Q(initiator=request.user) | Q(receiver=request.user)
        )
        serializer = ConversationListSerializer(instance=conversation_list, context={'request': request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        data = request.data
        user_id = data.get('user_id', None)
        
        try:
            participant = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'message': 'You cannot chat with a non existent user'}, status=status.HTTP_400_BAD_REQUEST)

        conversation = Conversation.objects.filter(
            Q(initiator=request.user, receiver=participant) |
            Q(initiator=participant, receiver=request.user)
        )
        if conversation.exists():
            return redirect(reverse('conversation-detail', args=[conversation.first().id]))
        else:
            conversation = Conversation.objects.create(initiator=request.user, receiver=participant)
            serializer = ConversationSerializer(instance=conversation, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class ConversationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_id):
        user = request.user
        conversation = Conversation.objects.filter(id=conversation_id)
        
        if not conversation.exists():
            return Response({'message': 'Conversation does not exist'}, status=status.HTTP_404_NOT_FOUND)
        elif not (conversation.first().initiator == user or conversation.first().receiver == user):
            return Response({'message': "Conversation not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = ConversationSerializer(instance=conversation.first(), context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
