from .models import *
from .serializers import *

BARTER_CONFIG = {
    'seed': {
             'model': SeedBarter,
        'serializer': SeedBarterSerializer
    },
    'plant': {
             'model': PlantBarter,
        'serializer': PlantBarterSerializer
    },
    'produce': {
             'model': ProduceBarter,
        'serializer': ProduceBarterSerializer
    },
    'material': {
             'model': MaterialBarter,
        'serializer': MaterialBarterSerializer
    },
    'tool': {
             'model': ToolBarter,
        'serializer': ToolBarterSerializer
    }
}
