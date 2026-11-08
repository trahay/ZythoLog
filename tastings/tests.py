import io
import shutil
import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import Beer, Brewery, Tasting

MEDIA = tempfile.mkdtemp()


def png(name="biere.png"):
    buf = io.BytesIO()
    Image.new("RGB", (10, 10), "orange").save(buf, "PNG")
    return SimpleUploadedFile(name, buf.getvalue(), content_type="image/png")


def payload(**extra):
    data = {
        "beer_name": "Punk IPA", "brewery_name": "BrewDog", "style": "IPA", "abv": "5.4",
        "date": "2026-11-01", "color_ebc": "12", "clarity": "limpide", "head_retention": "3",
        "aroma_intensity": "4", "aroma_malt": "1", "aroma_hop": "5", "aroma_yeast": "1",
        "aroma_descriptors": ["agrumes", "tropical"],
        "flavor_intensity": "4", "flavor_malt": "2", "flavor_hop": "4", "bitterness": "4",
        "sweetness": "1", "acidity": "0", "flavor_descriptors": ["resineux"],
        "body": "2", "carbonation": "4", "alcohol_warmth": "1", "astringency": "0",
        "off_flavors": [], "rating": "7.5", "notes": "Très houblonnée.",
    }
    data.update(extra)
    return data


@override_settings(MEDIA_ROOT=MEDIA)
class TastingTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def test_anonymous_create_with_photos(self):
        r = self.client.post(reverse("tastings:tasting_create"),
                             payload(author_name="Bob", photos=[png("a.png"), png("b.png")]))
        t = Tasting.objects.get()
        self.assertRedirects(r, t.get_absolute_url())
        self.assertIsNone(t.user)
        self.assertEqual(t.author_display, "Bob")
        self.assertEqual(t.photos.count(), 2)
        self.assertEqual(t.aroma_descriptors, ["agrumes", "tropical"])
        self.assertEqual(t.beer.style, "IPA")
        # L'auteur anonyme la retrouve et peut la modifier
        self.assertContains(self.client.get(reverse("tastings:my_tastings")), "Punk IPA")
        self.assertEqual(self.client.get(reverse("tastings:tasting_edit", args=[t.pk])).status_code, 200)

    def test_other_visitor_cannot_edit_but_secret_link_works(self):
        self.client.post(reverse("tastings:tasting_create"), payload())
        t = Tasting.objects.get()
        other = self.client_class()
        self.assertEqual(other.get(reverse("tastings:tasting_edit", args=[t.pk])).status_code, 403)
        other.get(reverse("tastings:tasting_claim", args=[t.edit_token]))
        self.assertEqual(other.get(reverse("tastings:tasting_edit", args=[t.pk])).status_code, 200)

    def test_beer_reused_case_insensitive_and_listing(self):
        self.client.post(reverse("tastings:tasting_create"), payload())
        self.client.post(reverse("tastings:tasting_create"),
                         payload(beer_name="punk ipa", brewery_name="brewdog", rating="9"))
        self.assertEqual(Beer.objects.count(), 1)
        self.assertEqual(Brewery.objects.count(), 1)
        beer = Beer.objects.with_stats().get()
        self.assertEqual(beer.tasting_count, 2)
        self.assertAlmostEqual(float(beer.avg_rating), 8.25)
        r = self.client.get(reverse("tastings:beer_detail", args=[beer.pk]))
        self.assertEqual(len(r.context["page"]), 2)
        r = self.client.get(reverse("tastings:beer_list"), {"q": "brewdog"})
        self.assertContains(r, "Punk IPA")

    def test_signup_claims_anonymous_tastings(self):
        self.client.post(reverse("tastings:tasting_create"), payload())
        self.client.post(reverse("tastings:signup"), {
            "username": "alice", "password1": "Houblon-2026!", "password2": "Houblon-2026!"})
        alice = User.objects.get(username="alice")
        self.assertEqual(Tasting.objects.get().user, alice)
        # Nouvelle dégustation connectée : rattachée directement au compte
        self.client.post(reverse("tastings:tasting_create"), payload(beer_name="Elvis Juice"))
        self.assertEqual(alice.tastings.count(), 2)
        r = self.client.get(reverse("tastings:my_tastings"))
        self.assertEqual(len(r.context["page"]), 2)

    def test_rating_bounds(self):
        r = self.client.post(reverse("tastings:tasting_create"), payload(rating="11"))
        self.assertEqual(r.status_code, 200)
        self.assertFalse(Tasting.objects.exists())

    def test_pages_render(self):
        self.client.post(reverse("tastings:tasting_create"), payload(photos=[png()]))
        t = Tasting.objects.get()
        for url in [reverse("tastings:home"), reverse("tastings:beer_list"),
                    t.get_absolute_url(), reverse("tastings:brewery_detail", args=[t.beer.brewery_id]),
                    reverse("tastings:tasting_create"), reverse("login"), reverse("tastings:signup")]:
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_delete_photo_and_tasting(self):
        self.client.post(reverse("tastings:tasting_create"), payload(photos=[png()]))
        t = Tasting.objects.get()
        photo = t.photos.get()
        self.client.post(reverse("tastings:tasting_edit", args=[t.pk]),
                         payload(delete_photos=[photo.pk]))
        self.assertEqual(t.photos.count(), 0)
        self.client.post(reverse("tastings:tasting_delete", args=[t.pk]))
        self.assertFalse(Tasting.objects.exists())
