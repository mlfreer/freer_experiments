from otree.api import *

import random
import math


doc = """
Your app description
"""

#----------------------------------------------------------
# CONSTANTS
class C(BaseConstants):
    NAME_IN_URL = 'procedures_T0'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 5

    BUDGET_SIZE = [3, 4, 5, 6, 7]

    # MENUS:
    MENU = [[[0 for i in range(0,10)] for j in range(0,10)] for k in range(0,10)]
    
    # MENU 0:
    MENU[0][0] = [10, 20, 30]
    MENU[0][1] = [30, 20, 10]

    # MENU 1:
    MENU[1][0] = [10, 20, 30, 40]
    MENU[1][1] = [40, 30, 20, 10]

    # MENU 2:
    MENU[2][0] = [10, 20, 30, 40, 50]
    MENU[2][1] = [50, 40, 30, 20, 10]

    # MENU 3:
    MENU[3][0] = [10, 20, 30, 40, 50, 60]
    MENU[3][1] = [60, 50, 40, 30, 20, 10]

    # MENU 3:
    MENU[3][0] = [10, 20, 30, 40, 50, 60, 70]
    MENU[3][1] = [70, 60, 50, 40, 30, 20, 10]
#----------------------------------------------------------



#----------------------------------------------------------
# MODELS:
class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    choice = models.IntegerField(default = -1)
    budget_id = models.IntegerField(default = -1)

    # storing sequence of actions as the strings recording the sequence of events:
    opened = models.StringField()
    chosen = models.StringField()
    closed = models.StringField()

    chosen_from_pair = models.StringField()
    closed_from_pair = models.StringField()


#----------------------------------------------------------

def creating_session(subsession: Subsession):
    for p in subsession.get_players():
        set_budgets_order(p)
    #----------------------------------------------------------

def set_budgets_order(player: Player):
    budgets = [i for i in range(0,C.NUM_ROUNDS)]
    random.shuffle(budgets)
    for p in player.in_all_rounds():
        p.budget_id = budgets[p.subsession.round_number-1]



#----------------------------------------------------------
# PAGES
class Decision(Page):
    form_model = 'player'
    form_fields = ['choice']

    @staticmethod
    def vars_for_template(player):
        budget_id = player.budget_id
        budget_array = range(0,C.BUDGET_SIZE[budget_id])
        lotteries = [[0 for i in range(0,3)  ] for j in range(0,C.BUDGET_SIZE[budget_id])]

        for j in range(0,C.BUDGET_SIZE[budget_id]):
            lotteries[j] = [j, C.MENU[budget_id][0][j], C.MENU[budget_id][1][j]]

        return dict(
            total_rounds = C.NUM_ROUNDS,
            round = player.subsession.round_number,
            budget = budget_array,
            budget_size = C.BUDGET_SIZE[budget_id],
            list_lotteries = lotteries
            )

    def live_method(player, data):
        t = data['type']

        if (t == 'opened'):
            player.opened = data['value']

        if (t == 'closed'):
            player.closed = data['value']

        if (t == 'chosen'):
            player.chosen = data['value']

        if (t == 'chosen_from_pair'):
            player.chosen_from_pair = data['value']

        if (t == 'closed_from_pair'):
            player.closed_from_pair = data['value']


class ResultsWaitPage(WaitPage):
    pass


class Results(Page):
    pass


page_sequence = [Decision, 
#                ResultsWaitPage, 
#                Results
                ]
