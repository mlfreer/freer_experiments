from otree.api import *


doc = """
Consent Form in German
"""

class C(BaseConstants):
    NAME_IN_URL = 'consent_form'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


# PAGES
class ConsentForm(Page):
    pass


page_sequence = [
    ConsentForm
]
