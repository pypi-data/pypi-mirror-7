from django.utils.importlib import import_module
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from ptree.session import create_session
import os.path
import ptree.test.run

class Command(BaseCommand):
    help = "pTree: Run the test bots for a session."
    args = '[session_name]'

    def handle(self, *args, **options):
        print 'Creating session...'
        if len(args) > 1:
            raise CommandError("Wrong number of arguments (expecting '{}')".format(self.args))

        if len(args) == 1:
            name = args[0]
        else:
            name = None

        session = create_session(name)
        session.label = '{} [test]'.format(session.label)
        session.save()

        ptree.test.run.run(session)






