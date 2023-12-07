from otree.api import *
import random
import math


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'AA_control'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    practice_time = 30
    real_time = 60

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


# PAGES
class PracticeTask(Page):
    timeout_seconds = C.practice_time
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
            prob_zero = C.prob_zero
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


page_sequence = [
    PracticeTask,
    Results
]
