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
    PLAYERS_PER_GROUP = 4
    NUM_ROUNDS = 5
    practice_time = 60#120
    real_time = 120#300

    # task parameters (matrix size):
    # y is universal
    all_y = 10 
    # x is type-specific
    small_x = 10 
    large_x = 15

    # Probability of zero appearing:
    prob_zero = .1

    # AA multiplier:
    multiplier = 1.5
    # tax rate
    tax = .5

    basic_wage = 1 # standard wage
    winner_wage = 2
    loser_wage = 0

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    discriminated = models.BooleanField() # False = 10x10, True = 15x10
    
    # my size of the matrix
    my_x = models.IntegerField(initial=10)
    my_y = models.IntegerField(initial=10)

    # earnings:
    my_wage = models.FloatField()
    num_correct = models.IntegerField(initial=0)
    aa_efforts = models.FloatField(default=0)
    earnings = models.FloatField()

    # is winner
    winner  = models.BooleanField(default = False)

    # compensation:
    compensation_type = models.IntegerField(min=0, max=3,initial=-1)
    # 0 = piece rate
    # 1 = competition
    # 2 = affirmative action
    # 3 = taxes
    # chosen task:
    chosen_compensation = models.IntegerField(min=0,max=2)
    alt1 = models.IntegerField(min=0,max=2)
    alt2 = models.IntegerField(min=0,max=2)
#-----------------------------------------------------------------------------------


#-----------------------------------------------------------------------------------
# FUNCTIONS


#-----------------------------------------------------------------------------------
def creating_session(session: Subsession):
    groups = session.get_groups()
    for g in groups:
        set_types(g)
        set_order(g)

    


def set_types(group: Group):
    numeric = [0, 1, 2, 3]
    random.shuffle(numeric)

    i=0
    for p in group.get_players():
        if numeric[i]<=1:
            p.discriminated = False
            p.my_x = C.small_x
            p.my_y = C.all_y 
        else:
            p.discriminated = True
            p.my_x = C.large_x
            p.my_y = C.all_y
        i=i+1


def set_order(group: Group):
    numeric = [0, 1, 2, 3]
    random.shuffle(numeric)

    g1 = group.in_round(1)
    g2 = group.in_round(2)
    g3 = group.in_round(3)
    g4 = group.in_round(4)

    for p in g1.get_players():
        p.compensation_type = numeric[0]
    for p in g2.get_players():
        p.compensation_type = numeric[1]
    for p in g3.get_players():
        p.compensation_type = numeric[2]
    for p in g4.get_players():
        p.compensation_type = numeric[3]

#    g1.compensation_type = numeric[0]
#    p2.compensation_type = numeric[1]
#    p3.compensation_type = numeric[2]



def set_payoff(player: Player):
    # retrieving the relevant round:
    for p in player.in_rounds(1,4):
        if p.compensation_type == player.compensation_type:
            me = p
    if me.discriminated == 1:
        player.aa_efforts = C.multiplier*player.num_correct
    else:
        player.aa_efforts = player.num_correct

    # retrieving efforts
    efforts = [0 for i in range(0,3)]
    aa_efforts = [0 for i in range(0,3)]
    i=0
    j=0
    for p in me.group.get_players():
        if p.id_in_group != me.id_in_group:
            efforts[i] = p.num_correct
            i=i+1
        if p.id_in_group != me.id_in_group:
            if p.discriminated==1:            
                aa_efforts[j] = p.num_correct*C.multiplier
            else:
                aa_efforts[j] = p.num_correct
            j=j+1


    efforts.sort(reverse = True)
    print(efforts)
    # determining the compensation:
    # basic tournament
    if player.compensation_type==1:
        if player.num_correct > efforts[1]:
            player.my_wage = C.winner_wage
            player.winner = True
        else:
            player.my_wage = C.loser_wage
            player.winner = False
    # piece rate
    elif player.compensation_type==0:
        player.my_wage = C.basic_wage
        player.winner = False
    # AA tournament
    elif player.compensation_type==2:
        if player.aa_efforts > aa_efforts[1]:
            player.my_wage = C.winner_wage
            player.winner = True
        else:
            player.my_wage = C.loser_wage
            player.winner = False
    elif player.compensation_type == 3:
    # TAX tournament
        if player.num_correct > efforts[1]:
            player.my_wage = C.winner_wage
            player.winner = True
        else:
            player.my_wage = C.loser_wage
            player.winner = False

    # computing the earnings
    player.earnings = player.my_wage*player.num_correct
    # computing the taxes:
    if player.compensation_type == 4:
        if player.winner == True:
            player.earnings = player.earnings*(1-C.tax)
        else:
            tax_earning = (efforts[0]+efforts[1])*C.winner_wage*C.tax/2
            player.earnings = player.earnings + tax_earning




#-----------------------------------------------------------------------------------
# PAGES
class InitialInstructions(Page):
    def is_displayed(player):
        return player.round_number == 1

class TaskInstructions(Page):
    def is_displayed(player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            discriminated = player.discriminated,
            all_y = C.all_y,
            small_x = C.small_x,
            large_x = C.large_x,
            )

class CompensationInstructions(Page):
    def is_displayed(player):
        return player.round_number <= C.NUM_ROUNDS-1

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            discriminated = player.discriminated,
            time = int(C.real_time/60),
            treatment = player.compensation_type,
            b_wage = C.basic_wage,
            w_wage = C.winner_wage,
            l_wage = C.loser_wage,
            task_number = player.round_number,
            all_y = C.all_y,
            small_x = C.small_x,
            large_x = C.large_x,
            multiplier = C.multiplier,
            tax = 100*C.tax
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
        return player.round_number <= C.NUM_ROUNDS

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
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def after_all_players_arrive(group: Group):
        players = group.get_players()
        for p in players:
            numeric = [0, 1, 2]
            random.shuffle(numeric)
            p.alt1 = numeric[0]
            p.alt2 = numeric[1]

class CompensationChoice(Page):
    form_model = 'player'
    form_fields = ['chosen_compensation']

    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        # retriving round number for tournament:
        aa_round = 0
        tournament_round = 0
        for p in player.in_previous_rounds():
            print(p.compensation_type==2)
            
            if p.compensation_type == 1:
                tournament_round = p.round_number
            if p.compensation_type == 2:
                aa_round = p.round_number
                
        return dict(
            task_number = player.round_number,
            discriminated = player.discriminated,
            all_y = C.all_y,
            small_x = C.small_x,
            large_x = C.large_x,
            time = int(C.real_time/60),
            b_wage = C.basic_wage,
            w_wage = C.winner_wage,
            l_wage = C.loser_wage,
            alt1 = player.alt1,
            alt2 = player.alt2,
            tournament_round = tournament_round,
            aa_round = aa_round
            )

class ResultsWaitPage(WaitPage):
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

    def after_all_players_arrive(group: Group):
        for p in group.get_players():
            set_payoff(p)

class Results(Page):
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

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
    InitialInstructions,
    TaskInstructions,
    PracticeTask,
    CompensationInstructions,
    TournamentWaitPage,
    CompensationChoice,
    RealTask,
    ResultsWaitPage,
    Results
]
