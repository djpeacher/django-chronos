from django.shortcuts import render
from django.urls import path
from django.contrib.auth.models import User
import secrets


def index_view(request):
    users = [
        User(username=f"demo_{secrets.token_hex(8)}", password="!")
        for _ in range(5000)
    ]
    User.objects.bulk_create(users)

    return render(request, "index.html", {"total": User.objects.count()})


urlpatterns = [
    path("", index_view, name="index"),
] 