from django.urls import path
from .views import show_home, all_export, game_export, user_export

urlpatterns = [
    path("", show_home, name="index"),
    path("all", all_export, name="index"),
    path("game/<id>/", game_export, name="index"),
    path("user/<id>/<player>/", user_export, name="index"),
]
