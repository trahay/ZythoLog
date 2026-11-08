from django import forms
from django.contrib.auth.forms import UserCreationForm

from . import choices as c
from .models import Beer, Brewery, Tasting


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={"accept": "image/*"}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single = super().clean
        if isinstance(data, (list, tuple)):
            return [single(d, initial) for d in data]
        return [single(data, initial)] if data else []


class RangeInput(forms.NumberInput):
    input_type = "range"
    template_name = "tastings/widgets/range.html"

    def __init__(self, labels, attrs=None):
        self.labels = labels
        super().__init__(attrs={"min": 0, "max": 5, "step": 1, **(attrs or {})})

    def get_context(self, name, value, attrs):
        ctx = super().get_context(name, value, attrs)
        ctx["widget"]["labels"] = self.labels
        return ctx


class ColorScaleInput(forms.Widget):
    """Curseur sur un dégradé de couleurs de bière (échelle EBC).

    La valeur est portée par un champ caché : tant que l'utilisateur n'a pas
    touché le curseur, la couleur reste « non renseignée ».
    """
    template_name = "tastings/widgets/color_scale.html"

    def get_context(self, name, value, attrs):
        ctx = super().get_context(name, value, attrs)
        ctx["widget"].update(
            min=c.EBC_MIN, max=c.EBC_MAX, gradient=c.ebc_gradient(),
            srm_hex=c.SRM_HEX, labels=c.EBC_LABELS,
            hex=c.ebc_to_hex(int(value)) if value not in (None, "") else "",
            label=c.ebc_label(int(value)) if value not in (None, "") else "",
        )
        return ctx


class ScaleInput(forms.Widget):
    """Curseur sur 5 points le long d'un dégradé, non renseigné tant qu'on n'y touche pas."""
    template_name = "tastings/widgets/scale.html"

    def __init__(self, choices, ticks, gradient, attrs=None):
        self.scale_choices, self.ticks, self.gradient = list(choices), ticks, gradient
        super().__init__(attrs)

    def get_context(self, name, value, attrs):
        ctx = super().get_context(name, value, attrs)
        labels = dict(self.scale_choices)
        value = int(value) if value not in (None, "") else None
        keys = [k for k, _ in self.scale_choices]
        ctx["widget"].update(
            value=value, min=min(keys), max=max(keys), mid=keys[len(keys) // 2],
            gradient=self.gradient, ticks=self.ticks, labels=labels,
            label=labels.get(value, ""),
        )
        return ctx


INTENSITY_FIELDS = [
    "aroma_intensity", "aroma_malt", "aroma_hop", "aroma_yeast",
    "flavor_intensity", "flavor_malt", "flavor_hop", "bitterness", "sweetness",
    "acidity", "alcohol_warmth", "astringency",
]


BEER_FIELDS = ["beer_name", "brewery_name", "style", "abv", "ibu"]


def get_or_update_beer(data):
    """Retrouve (sans tenir compte de la casse) ou crée la brasserie et la bière.

    Les infos renseignées (style, degré, IBU) mettent à jour la fiche de la bière.
    """
    brewery_name = data["brewery_name"].strip()
    brewery = (Brewery.objects.filter(name__iexact=brewery_name).first()
               or Brewery.objects.create(name=brewery_name))
    beer_name = data["beer_name"].strip()
    beer = Beer.objects.filter(name__iexact=beer_name, brewery=brewery).first()
    if beer is None:
        beer = Beer(name=beer_name, brewery=brewery)
    for field in ("style", "abv", "ibu"):
        if data.get(field) not in (None, ""):
            setattr(beer, field, data[field])
    beer.save()
    return beer


class BeerFieldsForm(forms.Form):
    """Champs décrivant une bière (créée à la volée si inconnue)."""
    beer_name = forms.CharField(label="Nom de la bière", max_length=200)
    brewery_name = forms.CharField(label="Brasserie", max_length=200)
    style = forms.ChoiceField(label="Style", choices=c.style_choices, required=False)
    abv = forms.DecimalField(label="Alcool (% vol.)", required=False, min_value=0,
                             max_value=70, decimal_places=1)
    ibu = forms.IntegerField(label="Amertume (IBU)", required=False, min_value=0)

    def keep_current_style(self, current):
        """Un style déjà enregistré mais absent de la liste reste sélectionnable."""
        if current and current not in c.ALL_STYLES and "style" in self.fields:
            self.fields["style"].choices = [
                *c.style_choices(), ("Style actuel (hors liste)", [(current, current)])]


class BeerForm(BeerFieldsForm):
    """Ajout d'une bière (par exemple pour imprimer son QR code avant de la vendre)."""

    def save(self):
        return get_or_update_beer(self.cleaned_data)


class TastingForm(forms.ModelForm, BeerFieldsForm):

    aroma_descriptors = forms.MultipleChoiceField(
        label="Descripteurs d'arômes", choices=c.DESCRIPTORS, required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    flavor_descriptors = forms.MultipleChoiceField(
        label="Descripteurs de saveurs", choices=c.DESCRIPTORS, required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    off_flavors = forms.MultipleChoiceField(
        label="Faux-goûts", choices=c.OFF_FLAVORS, required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    photos = MultipleImageField(label="Photos", required=False)

    class Meta:
        model = Tasting
        exclude = ["beer", "user", "edit_token"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "rating": forms.NumberInput(attrs={"min": 0, "max": 10, "step": 0.5}),
            "color_ebc": ColorScaleInput,
            "clarity": ScaleInput(c.CLARITY, c.CLARITY_TICKS, c.CLARITY_GRADIENT),
            "head_retention": ScaleInput(c.HEAD_RETENTION, c.HEAD_RETENTION_TICKS, c.HEAD_RETENTION_GRADIENT),
            "body": forms.RadioSelect,
            "carbonation": forms.RadioSelect,
            "finish": forms.RadioSelect,
            **{f: forms.Textarea(attrs={"rows": 2}) for f in [
                "appearance_notes", "aroma_notes", "flavor_notes", "mouthfeel_notes"]},
            "notes": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, user=None, beer=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Bière imposée (arrivée par un QR code) : ses infos ne sont pas modifiables
        self.fixed_beer = beer
        if beer is not None:
            for name in BEER_FIELDS:
                del self.fields[name]
        for name in INTENSITY_FIELDS:
            self.fields[name].widget = RangeInput(dict(c.INTENSITY))
            self.fields[name].required = False  # 0 par défaut (voir clean)
        # Les RadioSelect générés par Django ajoutent un choix vide « --------- »
        for name in ["body", "carbonation", "finish"]:
            self.fields[name].choices = [ch for ch in self.fields[name].choices if ch[0] != ""]
        # Un utilisateur connecté signe avec son compte : pas besoin de pseudo
        if user is not None and user.is_authenticated:
            del self.fields["author_name"]
        beer = self.instance.beer if self.instance.pk else None
        self.keep_current_style((beer.style if beer else "") or self.initial.get("style") or "")
        if beer:
            self.initial.update(beer_name=beer.name, brewery_name=beer.brewery.name,
                                style=beer.style, abv=beer.abv, ibu=beer.ibu)

    def clean(self):
        cleaned = super().clean()
        for name in INTENSITY_FIELDS:
            if cleaned.get(name) is None:
                cleaned[name] = 0
        return cleaned

    def save_beer(self):
        if self.fixed_beer is not None:
            return self.fixed_beer
        return get_or_update_beer(self.cleaned_data)

    def save(self, commit=True):
        self.instance.beer = self.save_beer()
        return super().save(commit)


class SignUpForm(UserCreationForm):
    email = forms.EmailField(label="Adresse e-mail", required=False)

    class Meta(UserCreationForm.Meta):
        fields = ("username", "email")


class BeerSearchForm(forms.Form):
    q = forms.CharField(label="Rechercher", required=False,
                        widget=forms.TextInput(attrs={"placeholder": "Bière, brasserie ou style…"}))
    style = forms.ChoiceField(
        label="Style", required=False,
        choices=lambda: [("", "Tous les styles")] + c.style_choices()[1:],
    )
