from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'procedures_T0'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 5

    BUDGET_SIZE = [6, 6, 6, 6, 6]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    choice = models.IntegerField(default = -1)


# PAGES
class Decision(Page):
    form_model = 'player'
    form_fields = ['choice']

    @staticmethod
    def vars_for_template(player):

        return dict(
            total_rounds = C.NUM_ROUNDS,
            round = player.subsession.round_number,
            budget = [0,1,2,3,4,5],
            budget_size = 6,
            )


class ResultsWaitPage(WaitPage):
    pass


class Results(Page):
    pass


page_sequence = [Decision, 
#                ResultsWaitPage, 
#                Results
                ]
