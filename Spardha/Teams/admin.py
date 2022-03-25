from django.contrib import admin
from .models import Game, Team, Contingent

class GameAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'game_type', 'min_players', 'max_players')
    search_fields = ('name', 'game_type')
    list_filter = ('game_type',)
admin.site.register(Game,GameAdmin)

class TeamAdmin(admin.ModelAdmin):
    list_display = (
        '__str__','college', 'captain_name', 'captain_phone', 'players_count')
    search_fields = ('captain_name', 'captain_phone')
    list_filter = ('game','user')

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super(TeamAdmin, self).get_search_results(request, queryset, search_term)
        try:
            for team in self.model.objects.all():
                if team.college().lower().find(search_term.lower()) != -1:
                    queryset = queryset | self.model.objects.filter(id=team.id)
                if team.game.name.lower().find(search_term.lower()) != -1:
                    queryset = queryset | self.model.objects.filter(id=team.id)
        except:
            pass
        return queryset, use_distinct
admin.site.register(Team,TeamAdmin)

class ContiAdmin(admin.ModelAdmin):
    list_display = (
        '__str__','leader_name', 'leader_contact_num', 'num_of_officials', 'num_of_boys','num_of_girls')
    search_fields = ('leader_name',)
    list_filter = ('college_rep',)

admin.site.register(Contingent,ContiAdmin)
