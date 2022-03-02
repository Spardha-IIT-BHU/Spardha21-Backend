from rest_framework import serializers
from .models import Game, Team, Player
from Authentication.models import UserAccount


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = "__all__"


class TeamSerializer(serializers.ModelSerializer):
    college_rep = serializers.EmailField()
    game = serializers.CharField()
    num_of_players = serializers.IntegerField()

    def save(self, **kwargs):
        data = self.validated_data
        game = Game.objects.get(name=data["game"])
        college_rep = UserAccount.objects.get(email=data["college_rep"])
        num_of_players = data["num_of_players"]

        team = Team.objects.create(
            game=game,
            college_rep=college_rep,
            num_of_players=num_of_players,
        )
        return team

    class Meta:
        model = Team
        fields = [
            "game.name",
            "college_rep.email",
            "num_of_players",
        ]


class PlayerSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    game = serializers.CharField()
    college_rep = serializers.EmailField()
    is_captain = serializers.BooleanField()

    def save(self, **kwargs):
        data = self.validated_data
        name = data["name"]
        game = Game.objects.get(name=data["game"])
        college_rep = UserAccount.objects.get(email=data["college_rep"])
        team = Team.objects.get(game=game, college_rep=college_rep)
        is_captain = data["is_captain"]

        player = Player.objects.create(
            name=name,
            team=team,
            is_captain=is_captain,
        )
        return player

    class Meta:
        model = Player
        fields = [
            "name",
            "team.game.name",
            "is_captain",
        ]
