from django.db import models
from Authentication.models import UserAccount
from django.core.validators import MinLengthValidator
from django.contrib.postgres.fields import ArrayField


class Game(models.Model):
    name = models.CharField(max_length=20)
    min_players = models.IntegerField()
    max_players = models.IntegerField()
    game_type = models.CharField(max_length=1)

    def __str__(self):
        return self.name+'_'+self.game_type


class Team(models.Model):
    # id = models.IntegerField(unique=True, primary_key=True)
    captain_name=models.CharField(max_length=40)
    captain_phone = models.CharField(max_length=10, validators=[MinLengthValidator(10)])
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    players = ArrayField(
            models.SlugField(max_length=50,blank=True),
            blank=True,
    )

    def __str__(self):
        return (self.game.name+"_"+self.game.game_type+"_" +
                self.user.institution_name)


class Contingent(models.Model):
    college_rep = models.OneToOneField(
        UserAccount,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    num_of_boys = models.IntegerField()
    num_of_girls = models.IntegerField()
    num_of_officials = models.IntegerField()
    leader_name = models.CharField(max_length=50)
    leader_contact_num = models.CharField(
        max_length=10, validators=[MinLengthValidator(10)])

    def __str__(self):
        return self.college_rep.institution_name
