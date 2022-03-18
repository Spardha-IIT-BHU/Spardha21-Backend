from rest_framework import serializers
from .models import Game, Team, Player, Contingent
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
        game = data["game"].split("_")
        name = game[0]
        game_type = game[1]
        game = Game.objects.get_object_or_404(name=name, game_type=game_type)
        college_rep = UserAccount.objects.get_object_or_404(email=data["college_rep"])
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
        team = Team.objects.get_object_or_404(id=data["team_id"])
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


class ContingentSerializer(serializers.ModelSerializer):
    college_rep = serializers.EmailField()
    num_of_boys = serializers.IntegerField()
    num_of_girls = serializers.IntegerField()
    leader_name = serializers.CharField()
    leader_contact_num = serializers.CharField()

    def save(self, **kwargs):
        data = self.validated_data
        college_rep = UserAccount.objects.get_object_or_404(email=data["college_rep"])
        num_of_boys = data["num_of_boys"]
        num_of_girls = data["num_of_girls"]
        leader_name = data['leader_name']
        leader_contact_num = data["leader_contact_num"]

        contingent = Contingent.objects.create(
            college_rep=college_rep,
            num_of_boys=num_of_boys,
            num_of_girls=num_of_girls,
            leader_name=leader_name,
            leader_contact_num=leader_contact_num,
        )
        return contingent

    class Meta:
        model = Contingent
        fields = "__all__"
