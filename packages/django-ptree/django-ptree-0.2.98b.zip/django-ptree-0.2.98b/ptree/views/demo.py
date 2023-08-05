from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseNotFound
import vanilla
import ptree.constants as constants
from ptree.sessionlib.models import Session
from ptree.session import create_session, demo_enabled_session_types
import threading

class DemoIndex(vanilla.View):

    @classmethod
    def url_pattern(cls):
        return r'^demo/$'

    def get(self, *args, **kwargs):
        session_types_and_urls = [(type, '/demo/{}/'.format(type)) for type in demo_enabled_session_types()]
        return render_to_response('ptree/demo.html', {'session_types_and_urls': session_types_and_urls})

def ensure_enough_spare_sessions(type):
    DESIRED_SPARE_SESSIONS = 3

    spare_sessions = Session.objects.filter(
        special_category=constants.special_category_demo,
        type=type,
        demo_already_used=False,
    ).count()

    # fill in whatever gap exists. want at least 3 sessions waiting.
    for i in range(DESIRED_SPARE_SESSIONS - spare_sessions):
        print 'Creating demo sessions: {}'.format(type)
        create_session(
            special_category=constants.special_category_demo,
            type=type
        )

def get_session(type):
    sessions = Session.objects.filter(
        special_category=constants.special_category_demo,
        type=type,
        demo_already_used=False
    )
    if sessions.exists():
        return sessions[:1].get()

class Demo(vanilla.View):

    @classmethod
    def url_pattern(cls):
        return r'^demo/(?P<session_type>\w+)/$'

    def get(self, *args, **kwargs):
        type=kwargs['session_type']

        if self.request.is_ajax():
            session = get_session(type)
            return HttpResponse(int(session is not None))

        t = threading.Thread(
            target=ensure_enough_spare_sessions,
            args=(type,)
        )
        t.start()

        session = get_session(type)
        if session:
            session.demo_already_used = True
            session.save()


            return render_to_response(
                'admin/StartLinks.html',
                {
                    'experimenter_url': self.request.build_absolute_uri(session.session_experimenter.start_url()),
                    'participant_urls': [self.request.build_absolute_uri(participant.start_url()) for participant in session.participants()],
                }
            )
        else:
            return render_to_response(
                'ptree/WaitPage.html',
                {
                    'SequenceViewURL': self.request.path,
                    'wait_page_title_text': 'Please wait',
                    'wait_page_body_text': 'Creating a session',
                }
            )