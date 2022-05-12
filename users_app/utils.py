# from .models import User
import jwt
import datetime
import decouple
from garden_barter_proj import settings

from .models import RefreshToken, User

def generate_test_user(UserModel: User, email: str, password: str, token_expiry: dict = None, **kwargs) -> 'User':
    '''Generate a User object and RefreshToken for that user.
    UserModel - One of the models from the users_app
    email - string
    password - string
    token_expiry - dict containing the time from creation to expiration for a token. {'hours': 1, 'minutes':1, 'seconds': 1}
    '''

    user, created = UserModel.objects.get_or_create(
        email=email,
        password=password,
    )

    if kwargs:
        for attr, value in kwargs.items():
            setattr(user, attr, value)

    user.save()

    refresh_token = Token(user, 'refresh', expiry=token_expiry)
    user_refresh_token = RefreshToken.objects.get_or_create(
        user=user, token=refresh_token)

    return user, refresh_token


class Token:
    '''
    user - User instance
    token_type (str): 'access' or 'refresh'
    expiry - (dict): Dictionary containing integers for the days, minutes, and seconds before the JWT expires
    extra_payload_items - (dict): Dictionary containing additional items to include in the JWT payload 
    '''

    def __init__(self, user, token_type: str = 'access', expiry: dict = None, **extra_payload_items) -> None:
        ACCESS_EXPIRY = {'days': 0, 'minutes': 1,
                         'seconds': 5, 'milliseconds': 0, 'microseconds': 0}
        REFRESH_EXPIRY = {'days': 7, 'minutes': 0,
                          'seconds': 0, 'milliseconds': 0, 'microseconds': 0}

        self.user = user
        self.token_type = token_type
        self.extra_payload_items = extra_payload_items
        self.expiry = expiry
        if expiry is None:
            self.expiry = ACCESS_EXPIRY if token_type == 'access' else REFRESH_EXPIRY
        self.token = self._generate_token()

    def _generate_token(self):
        '''Create a payload and attach to a JWT'''
        payload = {
            # id from User instance
            'user_id': self.user.id,
            # expiration date
            'exp': datetime.datetime.utcnow() + datetime.timedelta(
                days=self.expiry.get('days') or 0,
                minutes=self.expiry.get('minutes') or 0,
                seconds=self.expiry.get('seconds') or 0,
                milliseconds=self.expiry.get('milliseconds') or 0,
                microseconds=self.expiry.get('microseconds') or 0
            ),
            # initiated at date
            'iat': datetime.datetime.utcnow(),
        }

        # add extra kwargs to the jwt payload
        payload.update(self.extra_payload_items)

        # set encoding secret based on selected token type
        SECRET = settings.ACCESS_TOKEN_SECRET if self.token_type == 'access' else settings.REFRESH_TOKEN_SECRET

        # create jwt
        token = jwt.encode(
            payload,
            SECRET,
            algorithm='HS256'
        )
        self.token = token
        return token

    def get_payload(token: bytes, token_type: str = 'access') -> bool:
        SECRET = settings.ACCESS_TOKEN_SECRET if token_type == 'access' else settings.REFRESH_TOKEN_SECRET

        try:
            payload = jwt.decode(
                token,
                SECRET,
                algorithms=['HS256']
            )

            return payload

        except jwt.ExpiredSignatureError:
            return False

    def __repr__(self):
        return self.token
