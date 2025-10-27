from urllib.parse import parse_qs
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.db import close_old_connections

User = get_user_model()

@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    """
    Custom middleware that takes JWT token from the query string
    and authenticates the user for Channels.
    """

    async def __call__(self, scope, receive, send):
        # Close old db connections to prevent usage of timed out connections
        close_old_connections()

        # Get the query string (bytes), decode to str
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)

        token_list = query_params.get('token')
        if token_list:
            token = token_list[0]
            try:
                # Validate the token
                UntypedToken(token)
                # If valid, get user_id from token payload
                from rest_framework_simplejwt.authentication import JWTAuthentication
                validated_token = JWTAuthentication().get_validated_token(token)
                user_id = validated_token['user_id']
                scope['user'] = await get_user(user_id)
            except (InvalidToken, TokenError):
                scope['user'] = AnonymousUser()
        else:
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)