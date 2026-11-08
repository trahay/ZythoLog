from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_delete
from django.dispatch import receiver

from . import ownership
from .models import Photo, Tasting


@receiver(user_logged_in)
def claim_anonymous_tastings(sender, request, user, **kwargs):
    """À la connexion, rattache au compte les dégustations faites sans compte."""
    ids = ownership.session_ids(request)
    if ids:
        n = Tasting.objects.filter(pk__in=ids, user__isnull=True).update(user=user)
        request.session[ownership.SESSION_KEY] = []
        if n:
            from django.contrib import messages
            messages.info(request, f"{n} dégustation(s) anonyme(s) rattachée(s) à votre compte.")


@receiver(post_delete, sender=Photo)
def delete_photo_file(sender, instance, **kwargs):
    instance.image.delete(save=False)
