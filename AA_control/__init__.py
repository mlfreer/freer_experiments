from otree.api import *
import random
import math


doc = """
Your app description
"""

#-----------------------------------------------------------------------------------
# CLASSES
class C(BaseConstants):
    NAME_IN_URL = 'AA_control'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 4
    practice_time = 60
    real_time = 120

    # task parameters (matrix size):
    # y is universal
    all_y = 10 
    # x is type-specific
    blue_x = 10 
    red_x = 15

    # Probability of zero appearing:
    prob_zero = .1

    basic_wage = 1 # standard wage
    winner_wage = 2
    loser_wage = 0

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    discriminated = models.IntegerField(min=0, max=1) # min = blue, max = red
    
    # my size of the matrix
    my_x = models.IntegerField(initial=10)
    my_y = models.IntegerField(initial=10)

    # earnings:
    my_wage = models.FloatField()
    num_correct = models.IntegerField(initial=0)
    earnings = models.FloatField()


    # compensation:
    compensation_type = models.IntegerField(min=0, max=2)
    # chosen task:
    chosen_compensation = models.IntegerField(min=0,max=2)
    alt1 = models.IntegerField(min=0,max=2)
    alt2 = models.IntegerField(min=0,max=2)
#-----------------------------------------------------------------------------------


#-----------------------------------------------------------------------------------
# FUNCTIONS


#-----------------------------------------------------------------------------------
def creating_session(session: Subsession):
    players = session.get_players()
    for p in players:
        set_order(p)

def set_order(player: Player):
    numeric = [0, 1, 2]
    random.shuffle(numeric)

    p1 = player.in_round(1)
    p2 = player.in_round(2)
    p3 = player.in_round(3)

    p1.compensation_type = numeric[0]
    p2.compensation_type = numeric[1]
    p3.compensation_type = numeric[2]




#-----------------------------------------------------------------------------------
# PAGES
class TaskInstructions(Page):
    def is_displayed(player):
        return player.round_number == 1

class CompensationInstructions(Page):
    def is_displayed(player):
        return player.round_number <= 3

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            time = int(C.real_time/60),
            treatment = player.compensation_type,
            b_wage = C.basic_wage,
            w_wage = C.winner_wage,
            l_wage = C.loser_wage
            )


class PracticeTask(Page):
    timeout_seconds = C.practice_time
    template_name = './_templates/RET.html'

    def is_displayed(player):
        return player.round_number == 1

    @staticmethod
    def live_method(player, data):
        player.num_correct = data
        print('current number of correct answers', data)

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            x = range(0,player.my_x),
            y = range(0,player.my_y),
            len_x = player.my_x,
            len_y = player.my_y,
            prob_zero = C.prob_zero,
            time = int(C.practice_time/60)
            )

    @staticmethod
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.my_wage = C.basic_wage
            player.earnings = player.my_wage*player.num_correct

class RealTask(Page):
    def is_displayed(player):
        return player.round_number <= 3

    timeout_seconds = C.real_time
    template_name = './_templates/RET.html'

    @staticmethod
    def live_method(player, data):
        player.num_correct = data
        print('current number of correct answers', data)

    @staticmethod
    def vars_for_template(player: Player):

        return dict(
            x = range(0,player.my_x),
            y = range(0,player.my_y),
            len_x = player.my_x,
            len_y = player.my_y,
            prob_zero = C.prob_zero,
            time = int(C.practice_time/60)
            )

    @staticmethod
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.my_wage = C.basic_wage
            player.earnings = player.my_wage*player.num_correct

class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):

        return dict(
            x = range(0,player.my_x),
            y = range(0,player.my_y),
            len_x = player.my_x,
            len_y = player.my_y,
            prob_zero = C.prob_zero,
            num_correct = player.num_correct,
            my_wage = player.my_wage,
            earnings = player.earnings
            )

class CompensationChoice(Page):
    form_model = 'player'
    form_fields = ['chosen_compensation']

    def is_displayed(player):
        return player.round_number <= 4

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            time = int(C.real_time/60),
            treatment = player.compensation_type,
            b_wage = C.basic_wage,
            w_wage = C.winner_wage,
            l_wage = C.loser_wage
            )


page_sequence = [
    TaskInstructions,
    PracticeTask,
    CompensationInstructions,
    RealTask,
    CompensationChoice
#    Results
]
