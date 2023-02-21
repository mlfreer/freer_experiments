from otree.api import *
import random
import math
import decimal

author = 'Mikhail Freer'

doc = """
Beauty Contest Task (to elicit level-k thinking)
"""

#-----------------------------------------------------------------------------------
# MODELS
#-----------------------------------------------------------------------------------
class Constants(BaseConstants):
    name_in_url = 'BeautyContest'
    players_per_group = None
    num_rounds = 1

    # max reward
    bc_reward = 5


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    bc_guess = models.IntegerField(min=0,max=100)
    bc_earnings = models.IntegerField(min=0,max=5, initial=0)

#-----------------------------------------------------------------------------------
# FUNCTIONS
#-----------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------
# SESSION
# beauty contest computation:
def set_bc_results(subsession: Subsession):
    players = subsession.get_players()

    # counting the number of players:
    N=0
    for p in players:
        N=N+1

    # defining the vector of guesses
    guesses = [0 for i in range(0,N)]
    i=0
    for p in players:
        guesses[i] = p.bc_guess
        i=i+1

    print(guesses)

    target = decimal.Decimal(2/3)*(sum(guesses))/len(guesses)

    # defining the max distance:
    distance = [0 for i in range(0,N)]
    i=0
    for p in players:
        distance[i] = abs(target - guesses[i])
        i=i+1
    min_distance = min(distance)

    # defining the winners:
    winners = [0 for i in range(0,N)]
    i=0      
    for p in players:
        if distance[i] == min_distance:
            winners[i] = 1
        i=i+1
    r = random.randint(1,sum(winners))
    i=0
    j=1
    for p in players:
        if winners[i] == 1 and j==r:
            p.bc_earnings = Constants.bc_reward
        else:
            p.bc_earnings = 0

        p.payoff = p.bc_earnings

        if winners[i]==1:
            j=j+1
        i=i+1
#-----------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------
# PAGES
#-----------------------------------------------------------------------------------
# beauty contest task
class BeautyContestInstructions(Page):
    pass
    
class BeautyContestDecision(Page):
    form_model = 'player'
    form_fields = ['bc_guess']



class BeautyContestWaitPage(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def after_all_players_arrive(subsession: Subsession):
        set_bc_results(subsession)
        players = subsession.get_players()
        for p in players:
            p.participant.vars['bc_earnings'] = p.bc_earnings

# for testing purposes
class BeautyContestResults(Page):
    def vars_for_template(player: Player):
        return dict(
            earning = player.bc_earnings,
            guess = player.bc_guess
            )


#-----------------------------------------------------------------------------------
# PAGE SEQUENCE
#-----------------------------------------------------------------------------------
page_sequence = [# beuaty contest task
                BeautyContestInstructions,
                BeautyContestDecision,
                BeautyContestWaitPage,
#                BeautyContestResults
                ]
