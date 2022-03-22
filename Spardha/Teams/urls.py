from django.urls import path
from .views import (
    AllGamesView,
    AllTeamsView,
    TeamView,
    ContingentDetailView,
)


urlpatterns = [
    path("games/<int:id>/", AllGamesView.as_view(), name="get-all-games"),
    path("", AllTeamsView.as_view(), name="get-create-team"),
    path("<str:game>/", TeamView.as_view(), name="get-delete-team"),
    path("contingent/details/", ContingentDetailView.as_view(),
         name="contingent-details")
]
