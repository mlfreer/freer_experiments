from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'WelcomeScreen'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


# PAGES
class WelcomeScreen(Page):
    template_name = './WelcomeScreen/WelcomeScreen.html'


page_sequence = [WelcomeScreen]
