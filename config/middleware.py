from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
import jwt

from apps.user.models import User


@database_sync_to_async
def get_user(token):
    try:
        user_id= jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.SIMPLE_JWT['ALGORITHM']])['user_id']
    except jwt.exceptions.DecodeError:
        return AnonymousUser()
    except jwt.ExpiredSignatureError:
        return AnonymousUser()
    try:
        return AnonymousUser() if user_id is None else User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()


class TokenAuthMiddleware(BaseMiddleware):

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        token = scope['query_string'].decode().split('=')[-1]
        print(scope['query_string'].decode())
        scope['user'] = await get_user(token)
        return await super().__call__(scope, receive, send)
