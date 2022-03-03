from django.db import models
from Authentication.models import UserAccount


class Game(models.Model):
    name = models.CharField(max_length=20)
    min_players = models.IntegerField()
    max_players = models.IntegerField()
    game_type = models.CharField(max_length=1)

    def __str__(self):
        return self.name+'_'+self.game_type


class Team(models.Model):
    id = models.IntegerField(unique=True, primary_key=True)
    college_rep = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    num_of_players = models.IntegerField()

    def __str__(self):
        return self.game.name + self.college_rep.institution_name


class Player(models.Model):
    name = models.CharField(max_length=50)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    is_captain = models.BooleanField()

    def __str__(self):
        return self.name + ("_Captain" if self.is_captain else "")
