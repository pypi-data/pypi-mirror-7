from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Get username given a session id'

    def handle(self, session_key, **kwargs):
        session = Session.objects.get(session_key=session_key)
        uid = session.get_decoded().get('_auth_user_id')
        user = get_user_model().objects.get(pk=uid)
        self.stdout.write("%s %s (%s)" % (user.username, user.get_full_name(), user.email))

