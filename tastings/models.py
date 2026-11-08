import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg, Count
from django.urls import reverse
from django.utils import timezone

from . import choices as c


class Brewery(models.Model):
    name = models.CharField("nom", max_length=200, unique=True)
    country = models.CharField("pays", max_length=100, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "brasserie"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("tastings:brewery_detail", args=[self.pk])


class BeerQuerySet(models.QuerySet):
    def with_stats(self):
        return self.annotate(
            tasting_count=Count("tastings"), avg_rating=Avg("tastings__rating")
        )


class Beer(models.Model):
    name = models.CharField("nom", max_length=200)
    brewery = models.ForeignKey(
        Brewery, on_delete=models.PROTECT, related_name="beers", verbose_name="brasserie"
    )
    style = models.CharField("style", max_length=100, blank=True)
    abv = models.DecimalField(
        "alcool (% vol.)", max_digits=4, decimal_places=1, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(70)],
    )
    ibu = models.PositiveIntegerField("amertume (IBU)", null=True, blank=True)

    objects = BeerQuerySet.as_manager()

    class Meta:
        ordering = ["name"]
        verbose_name = "bière"
        constraints = [
            models.UniqueConstraint(fields=["name", "brewery"], name="unique_beer_per_brewery")
        ]

    def __str__(self):
        return f"{self.name} ({self.brewery})"

    def get_absolute_url(self):
        return reverse("tastings:beer_detail", args=[self.pk])


class Tasting(models.Model):
    beer = models.ForeignKey(
        Beer, on_delete=models.CASCADE, related_name="tastings", verbose_name="bière"
    )
    # Auteur : soit un compte, soit un simple pseudo (dégustation anonyme)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="tastings", verbose_name="utilisateur",
    )
    author_name = models.CharField("pseudo", max_length=100, blank=True)
    # Jeton secret permettant à un auteur sans compte de modifier sa fiche
    edit_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    date = models.DateField("date de dégustation", default=timezone.localdate)
    serving = models.CharField("conditionnement", max_length=20, choices=c.SERVING, blank=True)
    place = models.CharField("lieu", max_length=200, blank=True)

    # Vue
    color_ebc = models.PositiveSmallIntegerField(
        "couleur (EBC)", null=True, blank=True,
        validators=[MinValueValidator(c.EBC_MIN), MaxValueValidator(c.EBC_MAX)],
    )
    clarity = models.PositiveSmallIntegerField("transparence", choices=c.CLARITY, null=True, blank=True)
    head_color = models.CharField("couleur de la mousse", max_length=20, choices=c.HEAD_COLOR, blank=True)
    head_texture = models.CharField("texture de la mousse", max_length=20, choices=c.HEAD_TEXTURE, blank=True)
    head_retention = models.PositiveSmallIntegerField(
        "ténacité de la mousse", choices=c.HEAD_RETENTION, null=True, blank=True
    )
    appearance_notes = models.TextField("remarques sur l'apparence", blank=True)

    # Odorat
    aroma_intensity = models.PositiveSmallIntegerField(
        "intensité aromatique", choices=c.SCALE_INTENSITY, null=True, blank=True
    )
    aroma_impression = models.PositiveSmallIntegerField(
        "impression", choices=c.SCALE_IMPRESSION, null=True, blank=True
    )
    aroma_descriptors = models.JSONField("descripteurs d'arômes", default=list, blank=True)
    aroma_notes = models.TextField("remarques sur les arômes", blank=True)

    # Goût
    flavor_intensity = models.PositiveSmallIntegerField(
        "intensité des saveurs", choices=c.SCALE_INTENSITY, null=True, blank=True
    )
    flavor_impression = models.PositiveSmallIntegerField(
        "impression", choices=c.SCALE_IMPRESSION, null=True, blank=True
    )
    finish = models.CharField("longueur en bouche", max_length=10, choices=c.FINISH, blank=True)
    flavor_descriptors = models.JSONField("descripteurs de saveurs", default=list, blank=True)
    flavor_notes = models.TextField("remarques sur les saveurs", blank=True)

    # Toucher
    body = models.PositiveSmallIntegerField("corps", choices=c.BODY, null=True, blank=True)
    carbonation = models.PositiveSmallIntegerField(
        "carbonatation", choices=c.CARBONATION, null=True, blank=True
    )
    mouthfeel_sensations = models.JSONField("sensations", default=list, blank=True)
    mouthfeel_notes = models.TextField("remarques sur la sensation en bouche", blank=True)


    # « rating » : impression personnelle de 1 (pas pour moi) à 5 (délicieuse)
    rating = models.PositiveSmallIntegerField("impression personnelle", choices=c.PERSONAL_IMPRESSION)
    balance = models.PositiveSmallIntegerField(
        "ensemble et équilibre", choices=c.BALANCE, null=True, blank=True
    )
    notes = models.TextField("notes de dégustation", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        verbose_name = "dégustation"

    def __str__(self):
        return f"{self.beer.name} – {self.date:%d/%m/%Y} – {self.author_display}"

    def get_absolute_url(self):
        return reverse("tastings:tasting_detail", args=[self.pk])

    @property
    def author_display(self):
        if self.user:
            return self.user.get_username()
        return self.author_name or "Anonyme"

    @property
    def color_hex(self):
        return c.ebc_to_hex(self.color_ebc) if self.color_ebc is not None else ""

    @property
    def color_label(self):
        return c.ebc_label(self.color_ebc) if self.color_ebc is not None else ""

    def aroma_descriptor_labels(self):
        return [c.DESCRIPTOR_LABELS.get(k, k) for k in self.aroma_descriptors]

    def flavor_descriptor_labels(self):
        return [c.DESCRIPTOR_LABELS.get(k, k) for k in self.flavor_descriptors]

    def mouthfeel_sensation_labels(self):
        return [c.MOUTHFEEL_SENSATION_LABELS.get(k, k) for k in self.mouthfeel_sensations]


    def aroma_profile(self):
        return [
            (label, value) for label, value in [
                ("Intensité", self.aroma_intensity),
                ("Impression", self.aroma_impression),
            ] if value is not None
        ]

    def flavor_profile(self):
        return [
            (label, value) for label, value in [
                ("Intensité", self.flavor_intensity),
                ("Impression", self.flavor_impression),
            ] if value is not None
        ]


def photo_path(instance, filename):
    return f"photos/{instance.tasting.date:%Y/%m}/{uuid.uuid4().hex}_{filename}"


class Photo(models.Model):
    tasting = models.ForeignKey(Tasting, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField("photo", upload_to=photo_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["uploaded_at"]

    def __str__(self):
        return self.image.name
