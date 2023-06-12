from otree.api import *


doc = """
Your app description
"""

#-----------------------------------------------------------------------------------
# MODELS:
class C(BaseConstants):
    NAME_IN_URL = 'FinalResults'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    SHOW_UP_FEE = 5


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass
#-----------------------------------------------------------------------------------


#-----------------------------------------------------------------------------------
# PAGES:
class FinalResults(Page):
    def vars_for_template(player):
        return dict(
            treatment_earnings = cu(player.participant.vars['treatment_earnings']),
            bc_earnings = cu(player.participant.vars['bc_earnings']),
            risk_earnings = cu(player.participant.vars['risk_earnings']),
            total_earnings = cu(player.participant.vars['treatment_earnings'])+cu(player.participant.vars['bc_earnings'])+cu(player.participant.vars['risk_earnings']) + cu(C.SHOW_UP_FEE),
            show_up_fee = cu(C.SHOW_UP_FEE),
            code = player.participant.code
            )
#-----------------------------------------------------------------------------------


#-----------------------------------------------------------------------------------
# PAGE SEQUENCE:
page_sequence = [
                # final results
                FinalResults
]
#-----------------------------------------------------------------------------------