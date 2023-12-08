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
    PLAYERS_PER_GROUP = 2
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
    compensation_type = models.IntegerField(min=0, max=2,initial=-1)
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


def set_payoff(player: Player):
    # retrieving the relevant round:
    for p in player.in_rounds(1,3):
        if p.compensation_type == player.compensation_type:
            me = p

    # retrieving efforts
    efforts = [0 for i in range(0,3)]
    i=0
    for p in me.group.get_players():
        if p.id_in_group != me.id_in_group:
            efforts[i] = p.num_correct
            i=i+1

    efforts.sort(reverse = True)
    print(efforts)
    # determining the compensation:
    if player.compensation_type>0:
        if player.num_correct > efforts[1]:
            player.my_wage = C.winner_wage
        else:
            player.my_wage = C.loser_wage
    else:
        player.my_wage = C.basic_wage
    # computing the earnings
    player.earnings = player.my_wage*player.num_correct



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
        return player.round_number <= 4

    timeout_seconds = C.real_time
    template_name = './_templates/RET.html'

    @staticmethod
    def live_method(player, data):
        player.num_correct = data
        print('current number of correct answers', data)

    @staticmethod
    def vars_for_template(player: Player):
        if player.compensation_type == -1:
            player.compensation_type=player.chosen_compensation
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

class TournamentWaitPage(WaitPage):
    def is_displayed(player):
        return player.round_number == 4

    @staticmethod
    def after_all_players_arrive(group: Group):
        players = group.get_players()
        for p in players:
            numeric = [0, 1]
            random.shuffle(numeric)
            p.alt1 = numeric[0]
            p.alt2 = numeric[1]

class CompensationChoice(Page):
    form_model = 'player'
    form_fields = ['chosen_compensation']

    def is_displayed(player):
        return player.round_number == 4

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            time = int(C.real_time/60),
            b_wage = C.basic_wage,
            w_wage = C.winner_wage,
            l_wage = C.loser_wage,
            alt1 = player.alt1,
            alt2 = player.alt2
            )

class ResultsWaitPage(WaitPage):
    def is_displayed(player):
        return player.round_number == 4

    def after_all_players_arrive(group: Group):
        for p in group.get_players():
            set_payoff(p)

class Results(Page):
    def is_displayed(player):
        return player.round_number == 4

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            b_wage = C.basic_wage,
            w_wage = C.winner_wage,
            l_wage = C.loser_wage,
            num_correct = player.num_correct,
            my_wage = player.my_wage,
            earnings = player.earnings
            )


page_sequence = [
    TaskInstructions,
    PracticeTask,
    CompensationInstructions,
    TournamentWaitPage,
    CompensationChoice,
    RealTask,
    ResultsWaitPage,
    Results
]
