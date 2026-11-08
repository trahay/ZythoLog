from django.urls import path

from . import views

app_name = "tastings"

urlpatterns = [
    path("", views.home, name="home"),
    path("bieres/", views.beer_list, name="beer_list"),
    path("bieres/nouvelle/", views.beer_create, name="beer_create"),
    path("bieres/<int:pk>/", views.beer_detail, name="beer_detail"),
    path("bieres/<int:pk>/qrcode.svg", views.beer_qrcode, name="beer_qrcode"),
    path("bieres/<int:pk>/etiquettes/", views.beer_labels, name="beer_labels"),
    path("b/<int:pk>/", views.beer_scan, name="beer_scan"),
    path("brasseries/<int:pk>/", views.brewery_detail, name="brewery_detail"),
    path("degustations/nouvelle/", views.tasting_create, name="tasting_create"),
    path("degustations/mes-degustations/", views.my_tastings, name="my_tastings"),
    path("degustations/<int:pk>/", views.tasting_detail, name="tasting_detail"),
    path("degustations/<int:pk>/modifier/", views.tasting_edit, name="tasting_edit"),
    path("degustations/<int:pk>/supprimer/", views.tasting_delete, name="tasting_delete"),
    path("degustations/acces/<uuid:token>/", views.tasting_claim, name="tasting_claim"),
    path("compte/inscription/", views.signup, name="signup"),
]
