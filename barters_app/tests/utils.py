from users_app.models import User
from barters_app.models import *
from rest_framework_simplejwt.tokens import RefreshToken

def enrich_request(request, access_token):
    '''Ammend header data to the given request'''

    # if access_token:
    headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
          }

    request.headers = headers

    return request


# def populate_barters(self):
#     models = {
#         'seed': SeedBarter,
#         'plant': PlantBarter,
#         'produce': ProduceBarter,
#         'material': MaterialBarter,
#         'tool':ToolBarter
#     }

#     for i in range(3):
#         user = User.objects.create_user(
#             email=f"user_{i}@gardenbarter.com",
#             password='pass3412'
#         )

#         for barter_type in models:
#             Model=models[barter_type]
#             for i in range(3):
#                 Model.objects.create(
#                     creator=user,
#                     title=f'{barter_type} barter title {i}',
#                     description= f'{barter_type} barter description {i}',
#                     will_trade_for= f'item that will be traded {i}',
#                     is_free= False,
#                     cross_street_1= '456 Fake St.',
#                     cross_street_2= '876 Synthetic Ave',
#                     postal_code= '77777',
#                     barter_type=barter_type
#                 )


