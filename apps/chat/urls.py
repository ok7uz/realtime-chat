from django.urls import path

from apps.chat.views import ConversationListView, GetConversationView, StartConversationView


urlpatterns = [
    path('', ConversationListView.as_view(), name='conversations'),
    path('create/', StartConversationView.as_view(), name='create-conversation'),
    path('<uuid:conversation_id>/', GetConversationView.as_view(), name='get-conversation'),
]