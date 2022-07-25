from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.hello),
    path('leaderboard', views.leaderboard),
    path("submit", views.submit),
    path('history/<slug:username>', views.history),
    path('vote', views.vote),

    # TODO: Config URL Patterns
]