from otree.api import *

import random
from random import shuffle
import math


doc = """
Your app description
"""

#----------------------------------------------------------
# CONSTANTS
class C(BaseConstants):
    NAME_IN_URL = 'procedures_T1'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 20

    # POINTS:
    POINTS_X = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 14, 12, 8, 6, 4]
    POINTS_Y = [14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 2, 6, 14, 18, 22]


    # BUDGET SiZES:
    BUDGET_SIZE = [6,10,7,7,10,6,8,7,7,6,5,8,7,6,4,2,2,2,2,2]

    # MENUS:
    MENUS = [[0 for j in range(0,20)] for k in range(0,20)]
    MENUS[0] = [0,0,1,0,0,1,0,0,0,1,1,0,0,0,1,1,0,0]
    MENUS[1] = [0,1,0,1,1,1,1,0,1,0,0,1,0,0,1,1,1,0]
    MENUS[2] = [0,0,1,1,0,0,1,0,0,1,0,1,1,0,1,0,0,0]
    MENUS[3] = [0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,1,0,1]
    MENUS[4] = [1,0,1,1,0,1,1,0,1,0,0,1,0,1,0,0,1,1]
    MENUS[5] = [0,1,1,0,1,0,0,0,0,0,1,0,0,1,0,0,1,0]
    MENUS[6] = [1,0,1,0,1,1,0,1,0,1,0,1,0,0,0,0,0,1]
    MENUS[7] = [0,0,0,0,1,0,1,0,0,1,1,0,1,1,1,0,0,0]
    MENUS[8] = [1,1,0,0,1,0,0,1,1,0,1,0,1,0,0,0,0,0]
    MENUS[9] = [0,0,0,1,1,0,0,1,0,0,0,1,1,0,1,0,0,0]
    MENUS[10] = [0,0,1,0,0,0,0,0,1,0,1,0,1,0,0,0,1,0]
    MENUS[11] = [1,1,0,1,1,0,1,0,0,0,0,0,1,1,0,0,1,0]
    MENUS[12] = [0,1,1,0,0,0,1,0,0,0,0,1,1,1,0,1,0,0]
    MENUS[13] = [0,0,0,0,0,0,1,1,0,0,0,1,0,1,0,1,1,0]
    MENUS[14] = [0,0,0,0,1,0,0,0,0,0,0,1,1,1,0,0,0,0]
    MENUS[15] = [0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0]
    MENUS[16] = [1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0]
    MENUS[17] = [0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0]
    MENUS[18] = [0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0,0,0]
    MENUS[19] = [0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0]

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
    payment_round = models.IntegerField(default= -1)

    # storing sequence of actions as the strings recording the sequence of events:
    opened = models.StringField()
    chosen = models.StringField()
    closed = models.StringField()

    chosen_from_pair = models.StringField()
    closed_from_pair = models.StringField()

    # decision time:
    choice_times = models.FloatField(default=0,max_digits=5, decimal_places=2)


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

def compute_payoff(player: Player):
    player.payment_round = random.randint(1,C.NUM_ROUNDS)
    coin_flip = random.randint(0,1)
    p = player.in_round(player.payment_round)

    budget_id = p.budget_id
    temp_menu = [k for k in range(0,18) if C.MENUS[budget_id][k]!=0 ]
    temp_id = temp_menu[p.choice]

    if coin_flip == 0:
        player.payoff = cu(C.POINTS_X[temp_id])
    else:
        player.payoff = cu(C.POINTS_Y[temp_id])






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

        temp_menu = [k for k in range(0,18) if C.MENUS[budget_id][k]!=0 ]
        #print(temp_menu)
        for j in range(0,C.BUDGET_SIZE[budget_id]):
            temp_id = temp_menu[j] #C.MENUS[budget_id][j]
            lotteries[j] = [j, C.POINTS_X[temp_id], C.POINTS_Y[temp_id]]

        print(lotteries)
        shuffle(lotteries)
        print(lotteries)
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

        if (t == 'time'):
            player.choice_times = data['value']

    def before_next_page(player, timeout_happened):
        if player.round_number == C.NUM_ROUNDS:
            compute_payoff(player)



class ResultsWaitPage(WaitPage):
    wait_for_all_groups = True

    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS
 

class Results(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS


page_sequence = [Decision, 
                ResultsWaitPage, 
                Results
                ]
