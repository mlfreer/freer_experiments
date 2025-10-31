from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'SBC_consent_t2'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    # QUIZ ANSWERS:
    QUIZ_ANSWERS = [1,0,3]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


# PAGES
class Instructions(Page):
    @staticmethod
    def vars_for_template(player: Player):
        session = player.session
        participant = player.participant
        return dict(
            # Used in instr.html to avoid unsupported '+' expressions in templates
            example_sum=session.config['A_BAR'] + participant.x_draw
        )


class MyPage(Page):
    pass


class ResultsWaitPage(WaitPage):
    pass


class Results(Page):
    pass

page_sequence = [  
                MyPage]
