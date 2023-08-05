from importlib import import_module
client = import_module('ptree.test.client')

# public API

class ParticipantBot(client.ParticipantBot):

    def play(self):
        return super(ParticipantBot, self).play()

    def submit(self, ViewClass, data=None):
        return super(ParticipantBot, self).submit(ViewClass, data=None)

    def submit_with_invalid_input(self, ViewClass, data=None):
        return super(ParticipantBot, self).submit_with_invalid_input(ViewClass, data=None)

class ExperimenterBot(client.ExperimenterBot):

    def play(self):
        return super(ExperimenterBot, self).play()

    def submit(self, ViewClass, data=None):
        return super(ExperimenterBot, self).submit(ViewClass, data=None)

    def submit_with_invalid_input(self, ViewClass, data=None):
        return super(ExperimenterBot, self).submit_with_invalid_input(ViewClass, data=None)
