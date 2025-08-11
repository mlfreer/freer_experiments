from otree.api import *

import random
import pandas as pd
import numpy as np
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
    NUM_ROUNDS = 25

    # POINTS:
    POINTS_X = pd.read_csv('./_static/global/points.csv').x.values
    POINTS_Y = pd.read_csv('./_static/global/points.csv').y.values

    # NUMBER OF ALTERNATIVES:
    L = len(POINTS_X)

    # BUDGET SiZES:
    BUDGET_SIZE = pd.read_csv('./_static/global/budget_sizes.csv').N.values   # adding 5 budgets size 16

    # MENUS:
    MENUS = pd.read_csv('./_static/global/new_menus.csv').values.T
    # 25 real + 1 practice budget

    # QUIZ ANSWERS:
    QUIZ_ANSWERS = [2,3,0]
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

    # for PRACTICE ROUND storing sequence of actions as the strings recording the sequence of events:
    test_choice = models.IntegerField(default = -1)
    test_opened = models.StringField()
    test_chosen = models.StringField()
    test_closed = models.StringField()

    test_chosen_from_pair = models.StringField()
    test_closed_from_pair = models.StringField()

    # PRACTICE ROUND decision time:
    test_choice_times = models.FloatField(default=0,max_digits=5, decimal_places=2)

    # demographics:
    gender = models.IntegerField(initial=-1)
    british = models.IntegerField(initial=-1)
    age = models.IntegerField(intiial=-1)
    reasoning = models.StringField(required=False)

    # variables for the quiz answers:
    q1 = models.IntegerField()
    q2 = models.IntegerField()
    q3 = models.IntegerField()
    # model to count the quiz attempts
    quiz_attempts = models.IntegerField(initial = 0)
    return_study = models.IntegerField(initial = 0)
    # Prolific rule: 3 fails => return the study


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
class PracticeDecision(Page):
    form_model = 'player'
    form_fields = ['test_choice']

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player):
        budget_id = C.NUM_ROUNDS
        budget_array = range(0,C.BUDGET_SIZE[budget_id])
        lotteries = [[0 for i in range(0,3)  ] for j in range(0,C.BUDGET_SIZE[budget_id])]

        temp_menu = [k for k in range(0,C.L) if C.MENUS[budget_id][k]!=0 ]
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
            player.test_opened = data['value']

        if (t == 'closed'):
            player.test_closed = data['value']

        if (t == 'chosen'):
            player.test_chosen = data['value']

        if (t == 'chosen_from_pair'):
            player.test_chosen_from_pair = data['value']

        if (t == 'closed_from_pair'):
            player.test_closed_from_pair = data['value']

        if (t == 'time'):
            player.test_choice_times = data['value']

class Decision(Page):
    form_model = 'player'
    form_fields = ['choice']

    @staticmethod
    def vars_for_template(player):
        budget_id = player.budget_id
        budget_array = range(0,C.BUDGET_SIZE[budget_id])
        lotteries = [[0 for i in range(0,3)  ] for j in range(0,C.BUDGET_SIZE[budget_id])]

        temp_menu = [k for k in range(0,C.L) if C.MENUS[budget_id][k]!=0 ]
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
    wait_for_all_groups = False

    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS
 

class Survey(Page):
    template_name = './_static/global/ProceduresSurvey.html'

    form_model = 'player'
    form_fields = ['age', 'gender', 'british', 'reasoning']

    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

class Results(Page):
    template_name = './_static/global/ProceduresResults.html'

    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player):
        return dict(
            showup = player.session.config['participation_fee'],
            payment = player.payoff  #+ player.session.config['participation_fee']
            )


class FinalPage(Page):
    template_name = './_static/global/ProceduresFinalPage.html'

    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS
class PracticeRoundNotification(Page):
    template_name = './_static/global/PracticeRoundNotification.html'

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1


class RealRoundNotification(Page):
    template_name = './_static/global/RealRoundNotification.html'

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

class Instructions(Page):
#    template_name = './_static/global/RealRoundNotification.html'

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player):
        return dict(
            showup = player.session.config['participation_fee'],
            min_pay = cu(player.session.config['min_pay']),
            max_pay = cu(player.session.config['max_pay'])
            )

class ReturnStudy(Page):
    template_name =  './_static/global/ReturnStudy.html'

    @staticmethod
    def is_displayed(player):
        return player.return_study == 1
        
# Quiz to check whether subject understands the lotteries
class Quiz(Page):
    template_name = './_static/global/Procedures_Quiz.html'

    form_model = 'player'
    form_fields = ['q1','q2','q3']

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

    def error_message(player, value):
        if ((value['q1']!=C.QUIZ_ANSWERS[0]) or (value['q2']!=C.QUIZ_ANSWERS[1]) or (value['q3']!=C.QUIZ_ANSWERS[2])) and (player.return_study == 0):
            result = 'Wrong answer! Try again!'
            player.quiz_attempts = player.quiz_attempts + 1
            if player.quiz_attempts >= 2:
                player.return_study = 1
            return result

page_sequence = [Instructions,
                Quiz,
                ReturnStudy,
                PracticeRoundNotification,
                PracticeDecision,
                RealRoundNotification,
                Decision, 
                #ResultsWaitPage,
                Survey,
#                Results,
#                FinalPage
                ]
