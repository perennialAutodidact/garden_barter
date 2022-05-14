from django.core.management.base import BaseCommand

from barters_app.models import *
from users_app.models import User

class Command(BaseCommand):

    def handle(self, *args, **options):

        models = {
            'seed': SeedBarter,
            'plant': PlantBarter,
            'produce': ProduceBarter,
            'material': MaterialBarter,
            'tool':ToolBarter
        }

        for i in range(3):
            user = User.objects.create_user(
                email=f"user_{i}@gardenbarter.com",
                password='pass3412'
            )

            for barter_type in models:
                Model=models[barter_type]
                for i in range(3):
                    Model.objects.create(
                        creator=user,
                        title=f'{barter_type} barter title {i}',
                        description= f'{barter_type} barter description {i}',
                        will_trade_for= f'item that will be traded {i}',
                        is_free= False,
                        cross_street_1= '456 Fake St.',
                        cross_street_2= '876 Synthetic Ave',
                        postal_code= '77777',
                        barter_type=barter_type
                    )


