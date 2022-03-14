from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Game, Team, Player, Contingent
from .serializers import (
    GameSerializer,
    TeamSerializer,
    PlayerSerializer,
    ContingentSerializer,
)
from Authentication.models import UserAccount


class AllGamesView(generics.ListAPIView):
    serializer_class = GameSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, id):
        if id == 0:  # For Boys
            id = 'B'
        elif id == 1:  # For Girls
            id = 'G'
        else:  # Mixed
            id = 'M'
        # print(id)
        game = Game.objects.filter(game_type=id)
        serializer = self.get_serializer(game, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TeamCreateView(generics.GenericAPIView):
    serializer_class = TeamSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        college_rep = UserAccount.objects.filter(
            email=serializer.data["college_rep"])
        game = Game.objects.filter(name=serializer.data["game"].split(
            "_")[0], game_type=serializer.data["game"].split("_")[1])
        team = Team.objects.filter(college_rep=college_rep.last(),
                                   game=game.last()).first()
        response_data = {
            "id": team.id,
            "college_rep": team.college_rep.email,
            "game": team.game.name + '_' + team.game.game_type,
            "num_of_players": team.num_of_players
        }
        return Response(response_data, status=status.HTTP_200_OK)


class AllTeamsView(generics.ListAPIView):
    serializer_class = TeamSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request):
        # print(request.user)
        teams = Team.objects.filter(college_rep=request.user)
        serializer = self.get_serializer(teams, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TeamDetailView(generics.GenericAPIView):
    serializer_class = PlayerSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class getDetailView(generics.ListAPIView):
    serializer_class = PlayerSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, id):
        team = Team.objects.filter(id=id).first()
        players = Player.objects.filter(team=team)
        serializer = self.get_serializer(players, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ContingentDetailView(generics.GenericAPIView):
    serializer_class = ContingentSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get(self, request):
        # print(request.user)
        contingent = Contingent.objects.filter(college_rep=request.user)
        serializer = self.get_serializer(contingent.last())
        return Response(serializer.data, status=status.HTTP_200_OK)
