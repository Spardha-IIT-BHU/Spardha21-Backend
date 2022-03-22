from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Game, Team, Contingent
from .serializers import (
    GameSerializer,
    TeamSerializer,
    ContingentSerializer,
)
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
            return Response(serializer.data, status=status.HTTP_200_OK)
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
        request.data["email"]=request.user.email
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": "Team has been created"}, status=status.HTTP_200_OK)

class TeamView(generics.GenericAPIView):
    serializer_class = TeamSerializer
    permission_classes = (permissions.IsAuthenticated, )

    @swagger_auto_schema(
        responses={
            200: """{
                    "captain_name": ...
                    "captain_phone": ...
                    "game": ...
                    "players": ...
                    }""",
            404: """{"error":"Team not found"}""",
        }
    )
    def get(self, request, id):
        team = Team.objects.filter(id=id)
        if team.exists():
            serializer = self.get_serializer(team.last())
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error":"Team not found"},status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        responses={
            200: """{"success": "Team has been deleted"}""",
            204: """{"error":"Team not found"}""",
        }
    )
    def delete(self, request, id):
        team = Team.objects.filter(id=id)
        if team.exists():
            team.delete()
            return Response({"success": "Team has been deleted"}, status=status.HTTP_200_OK)
        return Response({"error":"Team not found"},status=status.HTTP_204_NO_CONTENT)