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


INTENSITY_FIELDS = [
    "aroma_intensity", "aroma_malt", "aroma_hop", "aroma_yeast",
    "flavor_intensity", "flavor_malt", "flavor_hop", "bitterness", "sweetness",
    "acidity", "alcohol_warmth", "astringency",
]


class TastingForm(forms.ModelForm):
    # Champs décrivant la bière (créée à la volée si inconnue)
    beer_name = forms.CharField(label="Nom de la bière", max_length=200)
    brewery_name = forms.CharField(label="Brasserie", max_length=200)
    style = forms.CharField(label="Style", max_length=100, required=False)
    abv = forms.DecimalField(label="Alcool (% vol.)", required=False, min_value=0,
                             max_value=70, decimal_places=1)
    ibu = forms.IntegerField(label="Amertume (IBU)", required=False, min_value=0)

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
            "head_retention": forms.RadioSelect,
            "body": forms.RadioSelect,
            "carbonation": forms.RadioSelect,
            "finish": forms.RadioSelect,
            **{f: forms.Textarea(attrs={"rows": 2}) for f in [
                "appearance_notes", "aroma_notes", "flavor_notes", "mouthfeel_notes"]},
            "notes": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        for name in INTENSITY_FIELDS:
            self.fields[name].widget = RangeInput(dict(c.INTENSITY))
            self.fields[name].required = False  # 0 par défaut (voir clean)
        # Les RadioSelect générés par Django ajoutent un choix vide « --------- »
        for name in ["head_retention", "body", "carbonation", "finish"]:
            self.fields[name].choices = [ch for ch in self.fields[name].choices if ch[0] != ""]
        # Un utilisateur connecté signe avec son compte : pas besoin de pseudo
        if user is not None and user.is_authenticated:
            del self.fields["author_name"]
        beer = self.instance.beer if self.instance.pk else None
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
        """Retrouve (sans tenir compte de la casse) ou crée la brasserie et la bière."""
        d = self.cleaned_data
        brewery_name = d["brewery_name"].strip()
        brewery = (Brewery.objects.filter(name__iexact=brewery_name).first()
                   or Brewery.objects.create(name=brewery_name))
        beer_name = d["beer_name"].strip()
        beer = Beer.objects.filter(name__iexact=beer_name, brewery=brewery).first()
        if beer is None:
            beer = Beer(name=beer_name, brewery=brewery)
        # Les infos renseignées (style, degré, IBU) mettent à jour la fiche de la bière
        for field in ("style", "abv", "ibu"):
            if d.get(field) not in (None, ""):
                setattr(beer, field, d[field])
        beer.save()
        return beer

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
