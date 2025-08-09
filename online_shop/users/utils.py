import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings
from .models import User


def generate_password_reset_token(user_id):
    sub = {
        'user_id': user_id,
        'exp': datetime.now(timezone.utc) + timedelta(days=1),
        'type': 'reset_password'
    }
    return jwt.encode(sub, settings.SECRET_KEY, algorithm='HS256')


def verify_token(token):
    try:
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        if decoded['type'] == 'reset_password':
            current_time = datetime.now(timezone.utc).timestamp()
            if decoded['exp'] > current_time:
                if User.objects.filter(id=decoded['user_id']).exists():
                    return decoded
        return 0
    except jwt.ExpiredSignatureError:
        return 0
    except jwt.InvalidTokenError:
        return 0