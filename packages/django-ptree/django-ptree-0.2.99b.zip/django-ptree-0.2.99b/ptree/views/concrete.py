from ptree.views.abstract import (
    NonSequenceUrlMixin,
    PTreeMixin,
    ParticipantUpdateView,
    LoadClassesAndUserMixin,
    load_session_user,
    WaitPageMixin,
)
import ptree.forms
from datetime import datetime
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseNotFound
import vanilla
from django.utils.translation import ugettext as _
import ptree.constants as constants
import ptree.sessionlib.models
import ptree.common
import ptree.models.participants
import django.utils.timezone
import threading

class RedirectToPageUserShouldBeOn(NonSequenceUrlMixin,
                                   LoadClassesAndUserMixin,
                                   PTreeMixin,
                                   vanilla.View):
    name_in_url = 'shared'

    def get(self, request, *args, **kwargs):
        return self.redirect_to_page_the_user_should_be_on()

    @load_session_user
    def dispatch(self, request, *args, **kwargs):
        return super(RedirectToPageUserShouldBeOn, self).dispatch(request, *args, **kwargs)

class OutOfRangeNotification(NonSequenceUrlMixin, PTreeMixin, vanilla.View):
    name_in_url = 'shared'


    def dispatch(self, request, *args, **kwargs):
        return HttpResponse('No more pages in this sequence.')

class WaitUntilAssignedToMatch(ParticipantUpdateView):
    """
    this is visited after Initialize, to make sure the participant has a match and treatment.
    the participant can be assigned at any time, but this is a safeguard,
    and therefore should be at the beginning of each subsession.
    Should it instead be called after InitializeSessionParticipant?
    Someday, we might want to shuffle participants dynamically,
    e.g. based on the results of the past game.
    """
    name_in_url = 'shared'

    def show_skip_wait(self):
        if self.match and self.treatment:
            return self.PageActions.skip
        return self.PageActions.wait

    def wait_page_body_text(self):
        return 'Waiting until participant is assigned to match and treatment.'

    def get_wait_page(self):
        """2/11/2014: same as parent method, but remove debug_values, which are not valid if the participant doesn't have
         a treatment assigned yet"""
        return render_to_response(
            self.wait_page_template_name,
            {
                'SequenceViewURL': self.wait_page_request_url(),
                'wait_page_body_text': self.wait_page_body_text(),
                'wait_page_title_text': self.wait_page_title_text()
            }
        )

class SessionExperimenterWaitUntilParticipantsAreAssigned(NonSequenceUrlMixin, WaitPageMixin, vanilla.View):

    def wait_page_title_text(self):
        return 'Please wait'

    def wait_page_body_text(self):
        return 'Assigning participants to matches and treatments'

    def show_skip_wait(self):
        if self.session.participants_assigned_to_treatments_and_matches:
            return self.PageActions.skip
        return self.PageActions.wait

    @classmethod
    def get_name_in_url(cls):
        return 'shared'


    def dispatch(self, request, *args, **kwargs):
        session_user_code = kwargs[constants.session_user_code]
        self.request.session[session_user_code] = {}

        self.session_user = get_object_or_404(
            ptree.sessionlib.models.SessionExperimenter,
            code=kwargs[constants.session_user_code]
        )

        self.session = self.session_user.session
        page_action = self.validated_show_skip_wait()

        if self.request_is_from_wait_page():
            return self.response_to_wait_page(page_action)
        else:
            # if the participant shouldn't see this view, skip to the next
            if page_action == self.PageActions.skip:
                return HttpResponseRedirect(self.session_user.me_in_first_subsession.start_url())
            elif page_action == self.PageActions.wait:
                return self.get_wait_page()

class InitializeSessionExperimenter(vanilla.View):


    @classmethod
    def url_pattern(cls):
        return r'^InitializeSessionExperimenter/(?P<{}>[a-z]+)/$'.format(constants.session_user_code)

    def redirect_to_next_page(self):
        return HttpResponseRedirect(SessionExperimenterWaitUntilParticipantsAreAssigned.url(self.session_user))

    def get(self, *args, **kwargs):
        session_user_code = kwargs[constants.session_user_code]
        self.request.session[session_user_code] = {}

        self.session_user = get_object_or_404(
            ptree.sessionlib.models.SessionExperimenter,
            code=kwargs[constants.session_user_code]
        )

        if self.session_user.session.participants_assigned_to_treatments_and_matches:
            return self.redirect_to_next_page()
        return render_to_response('ptree/experimenter/StartSession.html', {})

    def post(self, request, *args, **kwargs):
        self.session_user = get_object_or_404(
            ptree.sessionlib.models.SessionExperimenter,
            code=kwargs[constants.session_user_code]
        )

        # generate hash when the experimenter starts, rather than when the session was created
        # (since code is often updated after session created)
        session = self.session_user.session

        #FIXME: this causes an error OSError child_exception
        #if not session.git_hash:
        #    session.git_hash = ptree.common.git_hash()
        #    session.save()

        self.session_user.time_started = django.utils.timezone.now()

        t = threading.Thread(target=session.assign_participants_to_treatments_and_matches)
        t.start()
        return self.redirect_to_next_page()

class InitializeSessionParticipantMagdeburg(vanilla.View):
    """since magdeburg doesn't let you pass distinct URLs to each PC"""

    @classmethod
    def url_pattern(cls):
        return r'^InitializeSessionParticipantMagdeburg/$'

    def get(self, *args, **kwargs):
        session_user_code = self.request.GET[constants.session_user_code]
        session_user = get_object_or_404(ptree.sessionlib.models.SessionParticipant, code=session_user_code)

        return HttpResponseRedirect(session_user.start_url())



class InitializeSessionParticipant(vanilla.UpdateView):

    @classmethod
    def url_pattern(cls):
        return r'^InitializeSessionParticipant/(?P<{}>[a-z]+)/$'.format(constants.session_user_code)

    def get(self, *args, **kwargs):

        session_user_code = kwargs[constants.session_user_code]
        self.request.session[session_user_code] = {}

        session_user = get_object_or_404(ptree.sessionlib.models.SessionParticipant, code=session_user_code)

        session_user.visited = True
        session_user.time_started = django.utils.timezone.now()

        participant_label = self.request.GET.get(constants.session_participant_label)
        if participant_label is not None:
            session_user.label = participant_label

        if session_user.ip_address == None:
            session_user.ip_address = self.request.META['REMOTE_ADDR']

        session_user.save()

        return HttpResponseRedirect(session_user.me_in_first_subsession.start_url())

