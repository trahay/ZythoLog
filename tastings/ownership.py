"""Gestion de la propriété des dégustations, avec ou sans compte.

- Un utilisateur connecté possède les dégustations liées à son compte.
- Un visiteur anonyme possède les dégustations dont l'identifiant est stocké
  dans sa session (cookie). Il reçoit aussi un lien secret (jeton) qui lui
  permet de les retrouver depuis un autre navigateur.
- Lorsqu'il se connecte ou crée un compte, ses dégustations anonymes sont
  rattachées à son compte (voir signals.py).
"""

SESSION_KEY = "my_tastings"


def session_ids(request):
    return request.session.get(SESSION_KEY, [])


def remember(request, tasting):
    ids = session_ids(request)
    if tasting.pk not in ids:
        request.session[SESSION_KEY] = ids + [tasting.pk]


def forget(request, tasting):
    request.session[SESSION_KEY] = [i for i in session_ids(request) if i != tasting.pk]


def can_edit(request, tasting):
    if request.user.is_authenticated and tasting.user_id == request.user.pk:
        return True
    # Une fiche rattachée à un compte n'est modifiable que par ce compte
    return tasting.user_id is None and tasting.pk in session_ids(request)
