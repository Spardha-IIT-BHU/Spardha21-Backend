from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseNotFound, HttpResponse
from Teams.models import Game, Team
import csv

# Create your views here.
def user_data():from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseNotFound, HttpResponse
from Teams.models import Game, Team
import csv

# Create your views here.
def user_data():
    users = []

    for team in Team.objects.all():
        if team.captain_name!=""  and team.captain_name is not None:
            users.append(
                {
                    "id": team.id,
                    "name": team.captain_name,
                    "player": ("Captain"),
                    "institution_name": team.user.institution_name,
                    "game": team.game.name,
                    "members": len(team.players)+1,
                }
            )
        for player in team.players:
            if player!="" and player is not None: 
                users.append(
                    {
                        "id": team.id,
                        "name": player,
                        "player": ("Player"),
                        "institution_name": team.user.institution_name,
                        "game": team.game.name,
                        "members": len(team.players)+1,
                    }
                )
    return users


def game_data():
    games = []
    for game in Game.objects.all():
        games.append(
            {
                "id": game.id,
                "name": game.name,
                "type": game.game_type,
            }
        )
    return games


def show_home(request):
    context = {
        "usersdata": user_data(),
        "gamesdata": game_data(),
    }

    if request.user.is_authenticated and request.user.has_perm("Manager.view_manager"):
        return render(request, "base.html", context)
    return HttpResponseNotFound("<h1>You are not allowed to visit this page!!!</h1>")


def table_to_response(name, table):
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=" + name + ".csv"},
    )

    writer = csv.writer(response)
    for row in table:
        writer.writerow(row)
    return response


def user_export(request, id,player):
    if request.user.is_authenticated and request.user.has_perm("Manager.export_user"):
        team = get_object_or_404(Team, id=id)
        data = [["User Details"]]
        data = [
            ["Name", player],
            ["Role", ("Captain" if team.captain_name==player else "Player")],
            ["Institution Name", team.user.institution_name],
            ["Game", team.game.name],
            ["Total Members", len(team.players)+1],
        ]

        return table_to_response(player.replace(" ", ""), data)
    return HttpResponseNotFound("<h1>You are not allowed to visit this page!!!</h1>")


def game_export(request, id):
    if request.user.is_authenticated and request.user.has_perm("Manager.export_game"):
        game = get_object_or_404(Game, id=id)
        data = [["College Name", "Members", "Captain", "Captain phone"]]
        for i in range(1, game.max_players + 1):
            data[0].append("Player " + str(i))
        for team in Team.objects.filter(game=game):
            arr = [team.user.institution_name, len(team.players)+1, team.captain_name, team.captain_phone]
            for player in team.players:
                arr.append(player)
            data.append(arr)
        data.sort(key=lambda x: x[0])
        return table_to_response(game.name.replace(" ", "")+"_"+game.game_type, data)
    return HttpResponseNotFound("<h1>You are not allowed to visit this page!!!</h1>")


def all_export(request):
    if request.user.is_authenticated and request.user.has_perm("Manager.export_all"):
        data = [["Name", "Role", "Institution Name", "Game", "Members"]]
        for team in Team.objects.all():
            if team.captain_name!=""  and team.captain_name is not None:
                data.append(
                    [
                        team.captain_name,
                        ("Captain"),
                        team.user.institution_name,
                        team.game.name,
                        len(team.players)+1,
                    ]
                )
            for player in team.players:
                if player!="" and player is not None:
                    data.append(
                        [
                            player,
                            ("Player"),
                            team.user.institution_name,
                            team.game.name,
                            len(team.players)+1,
                        ]
                    )
        return table_to_response("AllUsers", data)
    return HttpResponseNotFound("<h1>You are not allowed to visit this page!!!</h1>")

def show_game(request, id):
    if request.user.is_authenticated and request.user.has_perm("Manager.view_game"):
        game = get_object_or_404(Game, id=id)
        all_team=[]
        for team in Team.objects.filter(game=game):
            arr=[]
            for player in team.players:
                arr.append(player)
            all_team.append({
                "college": team.user.institution_name,
                "members": len(team.players)+1,
                "captain": team.captain_name,
                "phone": team.captain_phone,
                "players": arr,
            })
        all_team.sort(key=lambda x: x["college"])
        context = {"gameid":id, "gamename": game.name+"("+game.game_type+")", "gamesdata": game_data(), "gamedata": all_team}
        return render(request, "base.html", context)
    return HttpResponseNotFound("<h1>You are not allowed to visit this page!!!</h1>")
