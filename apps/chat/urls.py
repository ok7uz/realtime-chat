from django.urls import path

from apps.chat.views import ConversationListView, ConversationView


urlpatterns = [
    path('', ConversationListView.as_view(), name='conversations'),
    path('<uuid:conversation_id>/', ConversationView.as_view(), name='conversation-detail'),
]
