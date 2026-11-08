import segno
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from . import choices as c
from . import ownership
from .forms import BeerForm, BeerSearchForm, SignUpForm, TastingForm
from .models import Beer, Brewery, Photo, Tasting


def paginate(request, qs, per_page=20):
    return Paginator(qs, per_page).get_page(request.GET.get("page"))


def home(request):
    return render(request, "tastings/home.html", {
        "recent": Tasting.objects.select_related("beer__brewery", "user")
                                 .prefetch_related("photos")[:8],
        "top_beers": Beer.objects.with_stats().filter(tasting_count__gt=0)
                                 .select_related("brewery").order_by("-avg_rating")[:5],
        "search_form": BeerSearchForm(),
    })


def beer_list(request):
    form = BeerSearchForm(request.GET)
    beers = Beer.objects.with_stats().select_related("brewery").order_by("name")
    q = form.data.get("q", "").strip()
    if q:
        beers = beers.filter(Q(name__icontains=q) | Q(brewery__name__icontains=q)
                             | Q(style__icontains=q))
    style = form.data.get("style", "")
    if style:
        beers = beers.filter(style=style)
    return render(request, "tastings/beer_list.html", {
        "page": paginate(request, beers), "search_form": form, "q": q, "style": style,
    })


def beer_detail(request, pk):
    beer = get_object_or_404(Beer.objects.with_stats().select_related("brewery"), pk=pk)
    tastings = beer.tastings.select_related("user").prefetch_related("photos")
    return render(request, "tastings/beer_detail.html", {
        "beer": beer, "page": paginate(request, tastings),
    })


def brewery_detail(request, pk):
    brewery = get_object_or_404(Brewery, pk=pk)
    return render(request, "tastings/brewery_detail.html", {
        "brewery": brewery, "beers": brewery.beers.with_stats().order_by("name"),
    })


def tasting_detail(request, pk):
    tasting = get_object_or_404(
        Tasting.objects.select_related("beer__brewery", "user").prefetch_related("photos"), pk=pk
    )
    can_edit = ownership.can_edit(request, tasting)
    return render(request, "tastings/tasting_detail.html", {
        "t": tasting,
        "can_edit": can_edit,
        "show_secret_link": can_edit and tasting.user_id is None,
    })


def _save_tasting(request, form, tasting=None):
    with transaction.atomic():
        tasting = form.save(commit=False)
        if request.user.is_authenticated and tasting.user_id is None:
            tasting.user = request.user
        tasting.save()
        for image in form.cleaned_data["photos"]:
            Photo.objects.create(tasting=tasting, image=image)
        to_delete = request.POST.getlist("delete_photos")
        if to_delete:
            for photo in tasting.photos.filter(pk__in=to_delete):
                photo.delete()
    return tasting


def tasting_form_context(form, **extra):
    return {"form": form,
            "breweries": Brewery.objects.values_list("name", flat=True),
            "beer_names": Beer.objects.values_list("name", flat=True).distinct(), **extra}


def tasting_create(request):
    # ?beer=<id> (lien « Déguster cette bière » ou QR code) : la bière est imposée
    beer = None
    beer_id = request.GET.get("beer", "")
    if beer_id.isdigit():
        beer = Beer.objects.filter(pk=beer_id).select_related("brewery").first()
    if request.method == "POST":
        form = TastingForm(request.POST, request.FILES, user=request.user, beer=beer)
        if form.is_valid():
            tasting = _save_tasting(request, form)
            if not request.user.is_authenticated:
                ownership.remember(request, tasting)
                messages.info(request,
                    "Dégustation enregistrée ! Vous n'êtes pas connecté·e : conservez le "
                    "lien secret ci-dessous pour la retrouver, ou créez un compte pour "
                    "y rattacher vos dégustations.")
            else:
                messages.success(request, "Dégustation enregistrée.")
            return redirect(tasting)
    else:
        form = TastingForm(user=request.user, beer=beer)
    return render(request, "tastings/tasting_form.html", tasting_form_context(form))


def tasting_edit(request, pk):
    tasting = get_object_or_404(Tasting.objects.select_related("beer__brewery"), pk=pk)
    if not ownership.can_edit(request, tasting):
        raise PermissionDenied
    if request.method == "POST":
        form = TastingForm(request.POST, request.FILES, instance=tasting, user=request.user)
        if form.is_valid():
            _save_tasting(request, form)
            messages.success(request, "Dégustation mise à jour.")
            return redirect(tasting)
    else:
        form = TastingForm(instance=tasting, user=request.user)
    return render(request, "tastings/tasting_form.html",
                  tasting_form_context(form, tasting=tasting))


def tasting_delete(request, pk):
    tasting = get_object_or_404(Tasting, pk=pk)
    if not ownership.can_edit(request, tasting):
        raise PermissionDenied
    if request.method == "POST":
        beer = tasting.beer
        ownership.forget(request, tasting)
        tasting.delete()
        messages.success(request, "Dégustation supprimée.")
        return redirect(beer)
    return render(request, "tastings/tasting_confirm_delete.html", {"t": tasting})


def tasting_claim(request, token):
    """Lien secret : redonne à un visiteur anonyme l'accès à sa dégustation."""
    tasting = get_object_or_404(Tasting, edit_token=token)
    if tasting.user_id is None:
        if request.user.is_authenticated:
            tasting.user = request.user
            tasting.save(update_fields=["user"])
            messages.success(request, "Cette dégustation est maintenant rattachée à votre compte.")
        else:
            ownership.remember(request, tasting)
            messages.success(request, "Vous pouvez de nouveau modifier cette dégustation.")
    return redirect(tasting)


def my_tastings(request):
    if request.user.is_authenticated:
        qs = request.user.tastings.all()
    else:
        qs = Tasting.objects.filter(pk__in=ownership.session_ids(request), user__isnull=True)
    qs = qs.select_related("beer__brewery").prefetch_related("photos")
    return render(request, "tastings/my_tastings.html", {"page": paginate(request, qs)})


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # déclenche le rattachement des dégustations anonymes
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            messages.success(request, f"Bienvenue {user.username} !")
            return redirect("tastings:my_tastings")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})


# --- Bières vendues : ajout d'une bière et QR code ---------------------------

@login_required
def beer_create(request):
    form = BeerForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        beer = form.save()
        messages.success(request, f"« {beer.name} » est enregistrée. Son QR code est affiché ci-dessous.")
        return redirect(beer)
    return render(request, "tastings/beer_form.html", {"form": form})


def beer_scan(request, pk):
    """Adresse courte encodée dans le QR code : ouvre le formulaire pré-rempli."""
    beer = get_object_or_404(Beer, pk=pk)
    return redirect(f"{reverse('tastings:tasting_create')}?beer={beer.pk}")


def beer_scan_url(request, beer):
    return request.build_absolute_uri(reverse("tastings:beer_scan", args=[beer.pk]))


def beer_qrcode(request, pk):
    beer = get_object_or_404(Beer, pk=pk)
    qr = segno.make(beer_scan_url(request, beer), error="m")
    response = HttpResponse(content_type="image/svg+xml")
    qr.save(response, kind="svg", scale=10, border=2, xmldecl=False, svgns=True)
    if request.GET.get("download"):
        response["Content-Disposition"] = f'attachment; filename="zytholog-{beer.pk}.svg"'
    return response

