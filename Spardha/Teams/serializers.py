from rest_framework import serializers
from .models import Game, Team, Contingent
from Authentication.models import UserAccount
from django.shortcuts import get_object_or_404
from django.contrib.postgres.fields import ArrayField


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = "__all__"

class TeamSerializer(serializers.ModelSerializer):
    captain_name=serializers.CharField()
    captain_phone = serializers.CharField()
    user = serializers.CharField(source='user.email')
    game = serializers.CharField()
    players = ArrayField(
            serializers.CharField(),
            blank=True,
    )

    def save(self, **kwargs):
        data = self.validated_data
        game = data["game"].split("_")
        name = game[0]
        game_type = game[1]
        game = get_object_or_404(Game, name=name, game_type=game_type)
        user = get_object_or_404(UserAccount,email=data["user"])
        if Team.objects.filter(user=user, game=game).exists():
            raise serializers.ValidationError("Team already exists")
        team = Team.objects.create(
            captain_name=data["captain_name"],
            captain_phone=data["captain_phone"],
            game=game,
            user=user,
            players=data["players"],
        )
        return team

    class Meta:
        model = Team
        fields = [
            "game",
            "user",
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
