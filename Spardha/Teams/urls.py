from django.urls import path
from .views import (
    AllTeamsView,
    TeamCreateView,
    TeamDetailView,
    AllGamesView,
    getDetailView,
    ContingentDetailView,
)


urlpatterns = [
    path("games/<int:id>/", AllGamesView.as_view(), name="get-all-games"),
    path("", AllTeamsView.as_view(), name="get-all-games"),
    path("create/", TeamCreateView.as_view(), name="team-create"),
    path("details/", TeamDetailView.as_view(), name="team-detail"),
    path("get-details/<int:id>/", getDetailView.as_view(),
         name="get-team-detail"),
    path("contingent/details/", ContingentDetailView.as_view(),
         name="contingent-details")
]
