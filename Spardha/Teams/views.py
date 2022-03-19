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
from drf_yasg.utils import swagger_auto_schema


class AllGamesView(generics.ListAPIView):
    serializer_class = GameSerializer
    permission_classes = (permissions.IsAuthenticated, )

    @swagger_auto_schema(
        responses={
            200: """{
                    "name": ...
                    "min_players": ...
                    "max_players": ...
                    "game_type": ...
                    }""",
            404: """{"error":"id not found,
                                    id = 0 for Boys
                                    id = 1 for Girls
                                    id = 2 for Mixed"}""",
        }
    )
    def get(self, request, id):
        if id == 0:  # For Boys
            id = 'B'
        elif id == 1:  # For Girls
            id = 'G'
        else:  # Mixed
            id = 'M'
        # print(id)
        game = Game.objects.filter(game_type=id)
        if(game.exists()):
            serializer = self.get_serializer(game, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class TeamCreateView(generics.GenericAPIView):
    serializer_class = TeamSerializer
    permission_classes = (permissions.IsAuthenticated, )

    @swagger_auto_schema(
        responses={
            200: """{
                        "id": team.id,
                        "college_rep": team.college_rep.email,
                        "game": team.game.name + '_' + team.game.game_type,
                        "num_of_players": team.num_of_players
                    }""",
        }
    )
    def post(self, request):
        try:
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
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class AllTeamsView(generics.ListAPIView):
    serializer_class = TeamSerializer
    permission_classes = (permissions.IsAuthenticated, )

    @swagger_auto_schema(
        responses={
            200: """[
                        {
                            "id": team.id,
                            "college_rep": team.college_rep.email,
                            "game": team.game.name + '_' + team.game.game_type,
                            "num_of_players": team.num_of_players
                        },
                        {
                            "id": team.id,
                            "college_rep": team.college_rep.email,
                            "game": team.game.name + '_' + team.game.game_type,
                            "num_of_players": team.num_of_players
                        }
                        ...
                    ]
                    """,
            404: """{"error":"No teams found"}""",
        }
    )
    def get(self, request):
        # print(request.user)
        teams = Team.objects.filter(college_rep=request.user)
        if(teams.exists()):
            serializer = self.get_serializer(teams, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class TeamDetailView(generics.GenericAPIView):
    serializer_class = PlayerSerializer
    permission_classes = (permissions.IsAuthenticated, )

    @swagger_auto_schema(
        responses={
            200: """{
                        "name": ...,
                        "team_id": integer,
                        "is_captain": boolean,
                    }""",
        }
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class getDetailView(generics.ListAPIView):
    serializer_class = PlayerSerializer
    permission_classes = (permissions.IsAuthenticated, )

    @swagger_auto_schema(
        responses={
            200: """[
                        {
                            "name": ...,
                            "team_id": integer,
                            "is_captain": boolean,
                        },
                            {
                            "name": ...,
                            "team_id": integer,
                            "is_captain": boolean,
                        },
                        ...
                    ]
                    """,
            404: """{"error":"Team not found"}""",
        }
    )
    def get(self, request, id):
        team = Team.objects.filter(id=id).first()
        if(team.exists()):
            players = Player.objects.filter(team=team)
            serializer = self.get_serializer(players, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class ContingentDetailView(generics.GenericAPIView):
    serializer_class = ContingentSerializer
    permission_classes = (permissions.IsAuthenticated, )

    @swagger_auto_schema(
        responses={
            200: """{
                "college_rep": college_rep.email,
                "num_of_boys": integer,
                "num_of_girls": integer,
                "leader_name": ....,
                "leader_contact_num": ....,
                }""",
        }
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={
            200: """{
                "college_rep": college_rep.email,
                "num_of_boys": integer,
                "num_of_girls": integer,
                "leader_name": ....,
                "leader_contact_num": ....,
                }""",
            404: """{"error":"Contingent not found"}""",
        }
    )
    def get(self, request):
        # print(request.user)
        contingent = Contingent.objects.filter(college_rep=request.user)
        if contingent.exists():
            serializer = self.get_serializer(contingent.last())
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        responses={
            204: """{"delete": "Contingent has been deleted"}""",
        }
    )
    def delete(self, request):
        contingent = Contingent.objects.filter(college_rep=request.user)
        if contingent.exists():
            contingent.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
