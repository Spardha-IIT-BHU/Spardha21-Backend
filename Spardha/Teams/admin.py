from django.contrib import admin
from .models import Game, Team, Player, Contingent

admin.site.register(Game)
admin.site.register(Team)
admin.site.register(Player)
admin.site.register(Contingent)
