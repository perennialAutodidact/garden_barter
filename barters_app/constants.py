from .models import *
from .serializers import *

BARTER_CONFIG = {
    'seed_barter': {
             'model': SeedBarter,
        'serializer': SeedBarterSerializer
    },
    'plant_barter': {
             'model': PlantBarter,
        'serializer': PlantBarterSerializer
    },
    'produce_barter': {
             'model': ProduceBarter,
        'serializer': ProduceBarterSerializer
    },
    'material_barter': {
             'model': MaterialBarter,
        'serializer': MaterialBarterSerializer
    },
    'tool_barter': {
             'model': ToolBarter,
        'serializer': ToolBarterSerializer
    }
}
