from otree.api import *
import random
import math
import decimal

author = 'Mikhail Freer'

doc = """
Risk Elicitation Task
"""


#-----------------------------------------------------------------------------------
# MODELS
#-----------------------------------------------------------------------------------
class Constants(BaseConstants):
    name_in_url = 'RiskElicitation'
    players_per_group = None
    num_rounds = 1

    # risk constants:
    risk_max = 15
    risk_min = 1
    risk_safe = 10
    risk_prob_winning = .5
    risk_prob_paying = .1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # Risk elicitation task
    risk_choice = models.IntegerField(min=0,max=1) # choice of the option in risk elicitation task 0 - safe, 1 - risky
    risk_earnings = models.IntegerField(min=0,max=20)

    
#-----------------------------------------------------------------------------------
# FUNCTIONS
#-----------------------------------------------------------------------------------
def set_risk_results(player: Player):
    #setting up the default:
    player.risk_earnings = 0
    # defining the payoffs:
    r1 = random.uniform(0,1)
    if r1<= Constants.risk_prob_paying:
        player.risk_earnings = Constants.risk_min
        if player.risk_choice == 0:
            player.risk_earnings = Constants.risk_safe
        else:
            r2 = random.uniform(0,1)
            if r2<=Constants.risk_prob_winning:
                player.risk_earnings = Constants.risk_max    
    player.payoff = player.risk_earnings


#-----------------------------------------------------------------------------------
# PAGES
#-----------------------------------------------------------------------------------
# risk elicitation instructions:
class RiskElicitationInstructions(Page):
    template_name = './risk_elicitation/RiskElicitationInstructions_DE.html'

    def vars_for_template(player: Player):
        return dict(
            high_payoff = Constants.risk_max,
            low_payoff = Constants.risk_min,
            safe_payoff = Constants.risk_safe,
            payment_probability = Constants.risk_prob_paying*100,
            )


class RiskElicitationDecision(Page):
    template_name = './risk_elicitation/RiskElicitationDecision_DE.html'
    form_model = 'player'
    form_fields = ['risk_choice']

    def vars_for_template(player: Player):
        return dict(
            high_payoff = Constants.risk_max,
            low_payoff = Constants.risk_min,
            safe_payoff = Constants.risk_safe,
            payment_probability = Constants.risk_prob_paying*100,
            )

class RiskElicitationWaitPage(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def after_all_players_arrive(subsession: Subsession):
        players = subsession.get_players()
        for p in players:
            set_risk_results(p)
            p.participant.vars['risk_earnings'] = p.risk_earnings

# temporary results page
class RiskElicitationResults(Page):
    template_name = './risk_elicitation/RiskElicitationResults_DE.html'
    def vars_for_template(player: Player):
        print(player.participant.vars)
        return dict(
            risk_earning = player.risk_earnings,
#            bc_earning = player.participant.vars['bc_earnings'],
            choice = player.risk_choice,
            )

#-----------------------------------------------------------------------------------
# PAGE SEQUENCE
#-----------------------------------------------------------------------------------
page_sequence = [
                # risk elicitation task
                RiskElicitationInstructions,
                RiskElicitationDecision,
                RiskElicitationWaitPage,
#                RiskElicitationResults
]
