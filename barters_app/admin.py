from django.contrib import admin

from .models import (Barter, MaterialBarter, PlantBarter, ProduceBarter,
                     SeedBarter, ToolBarter)


admin.site.register([Barter, MaterialBarter, PlantBarter, ProduceBarter,
                     SeedBarter, ToolBarter])