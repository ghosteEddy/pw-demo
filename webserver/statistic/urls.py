from django.urls import path

from . import views

urlpatterns = [
    # /update-onemin
    path("<str:symbol>/update_onemin", views.update_onemin, name="update_onemin"),
    path(
        "<str:symbol>/fetch_onemin",
        views.get_onemin,
        name="fetch_period",
    ),
]
