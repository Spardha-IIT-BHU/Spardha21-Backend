from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Game, Team, Contingent
from .serializers import (
    GameSerializer,
    TeamSerializer,
    TeamUpdateSerializer,
    ContingentSerializer,
)
from drf_yasg.utils import swagger_auto_schema
from scripts.team_registration import UsersSheet


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
            data=serializer.data
            data.sort(key=lambda x: x.get('name'))
            return Response(data, status=status.HTTP_200_OK)
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
                "num_of_officials": integer,
                "leader_name": ....,
                "leader_contact_num": ....,
                }""",
        }
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        UsersSheet.update_user(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={
            200: """{
                "college_rep": college_rep.email,
                "num_of_boys": integer,
                "num_of_girls": integer,
                "num_of_officials": integer,
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
        UsersSheet.update_user(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AllTeamsView(generics.ListAPIView):
    serializer_class = TeamSerializer
    permission_classes = (permissions.IsAuthenticated, )

    @swagger_auto_schema(
        responses={
            200: """[{
                    "captain_name": ...
                    "captain_phone": ...
                    "game": ...
                    "players": ...
                    }]""",
            404: """{"error":"No teams found"}""",
        }
    )
    def get(self, request):
        team = Team.objects.filter(user=request.user)
        if team.exists():
            serializer = self.get_serializer(team, many=True)
            data=serializer.data
            data.sort(key=lambda x: x.get('game'))
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({"error":"No teams found"},status=status.HTTP_404_NOT_FOUND)
    
    @swagger_auto_schema(
        responses={
            200: """{"success": "Team has been created"}""",
            404: """{"error":"Game not found"}
                    {"error":"Team already exists"}""",
        }
    )
    def post(self,request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user)
        return Response({"success": "Team has been created"}, status=status.HTTP_200_OK)

class TeamView(generics.GenericAPIView):
    serializer_class = TeamUpdateSerializer
    permission_classes = (permissions.IsAuthenticated, )

    @swagger_auto_schema(
        responses={
            200: """{"success":"Team Details Modified"}""",
            404: """{"error":"Team not found"}""",
        }
    )
    def put(self, request, game):
        game=Game.objects.get(name=game.split('_')[0],game_type=game.split('_')[1])
        team = Team.objects.filter(game=game, user=request.user)
        if team.exists():
            if "captain_name" in request.data:
                team.update(captain_name=request.data["captain_name"])
            if "captain_phone" in request.data:
                team.update(captain_phone=request.data["captain_phone"])
            if "players" in request.data:
                team.update(players=request.data["players"])
            return Response({"success":"Team Details Modified"}, status=status.HTTP_200_OK)
        else:
            return Response({"error":"Team not found"},status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        responses={
            200: """{"success": "Team has been deleted"}""",
            204: """{"error":"Team not found"}""",
        }
    )
    def delete(self, request, game):
        game=Game.objects.get(name=game.split('_')[0],game_type=game.split('_')[1])
        team = Team.objects.filter(game=game, user=request.user)
        if team.exists():
            team.delete()
            return Response({"success": "Team has been deleted"}, status=status.HTTP_200_OK)
        return Response({"error":"Team not found"},status=status.HTTP_204_NO_CONTENT)