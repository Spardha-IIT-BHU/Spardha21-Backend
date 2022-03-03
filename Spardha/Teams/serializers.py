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
    # game_type = serializers.CharField()

    def save(self, **kwargs):
        data = self.validated_data
        game = data["game"].split("_")
        name = game[0]
        print(name)
        game_type = game[1]
        game = Game.objects.get(name=name, game_type=game_type)
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
            "game",
            "college_rep",
            "num_of_players",
        ]


class PlayerSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    team_id = serializers.IntegerField()
    is_captain = serializers.BooleanField()

    def save(self, **kwargs):
        data = self.validated_data
        name = data["name"]
        team = Team.objects.get(id=data["team_id"])
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
            "team_id",
            "is_captain",
        ]
