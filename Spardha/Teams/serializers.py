from rest_framework import serializers
from .models import Game, Team, Contingent
from Authentication.models import UserAccount
from django.shortcuts import get_object_or_404
from django.contrib.postgres.fields import ArrayField


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = "__all__"

class TeamUpdateSerializer(serializers.ModelSerializer):
    captain_name=serializers.CharField(max_length=40)
    captain_phone = serializers.CharField(max_length=40)
    players = ArrayField(
            serializers.CharField(max_length=50),
    )
    
    class Meta:
        model = Team
        fields = [
            "captain_name",
            "captain_phone",
            "players",
        ]

class TeamSerializer(serializers.ModelSerializer):
    captain_name=serializers.ReadOnlyField()
    captain_phone = serializers.ReadOnlyField()
    game = serializers.CharField()
    players = serializers.ReadOnlyField()

    def save(self, user, **kwargs):
        data = self.validated_data
        try:
            game = data["game"].split("_")
            name = game[0]
            game_type = game[1]
            game = Game.objects.get(name=name, game_type=game_type)
        except:
            raise serializers.ValidationError("Invalid Game Name")
        if Team.objects.filter(user=user, game=game).exists():
            raise serializers.ValidationError("Team already exists")
        team = Team.objects.create(
            game=game,
            user=user,
            captain_name="",
            captain_phone="",
            players=["" for i in range(game.max_players)],
        )
        return team

    class Meta:
        model = Team
        fields = [
            "game",
            "captain_name",
            "captain_phone",
            "players",
        ]


class ContingentSerializer(serializers.ModelSerializer):
    college_rep = serializers.EmailField()
    num_of_boys = serializers.IntegerField()
    num_of_girls = serializers.IntegerField()
    num_of_officials = serializers.IntegerField()
    leader_name = serializers.CharField()
    leader_contact_num = serializers.CharField()

    def save(self, **kwargs):
        data = self.validated_data
        college_rep = get_object_or_404(UserAccount, email=data["college_rep"])
        num_of_boys = data["num_of_boys"]
        num_of_girls = data["num_of_girls"]
        num_of_officials = data["num_of_officials"]
        leader_name = data['leader_name']
        leader_contact_num = data["leader_contact_num"]

        contingent = Contingent.objects.create(
            college_rep=college_rep,
            num_of_boys=num_of_boys,
            num_of_girls=num_of_girls,
            num_of_officials=num_of_officials,
            leader_name=leader_name,
            leader_contact_num=leader_contact_num,
        )
        return contingent

    class Meta:
        model = Contingent
        fields = "__all__"
