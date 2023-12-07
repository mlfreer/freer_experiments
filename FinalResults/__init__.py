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

    SHOW_UP_FEE = 6


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    reasoning = models.StringField(required = False)
#-----------------------------------------------------------------------------------


#-----------------------------------------------------------------------------------
# PAGES:
class Survey(Page):
    template_name = './FinalResults/Survey_DE.html'
    form_model = 'player'
    form_fields = ['reasoning']

class FinalResults(Page):
    template_name = './FinalResults/FinalResults_DE.html'
    def vars_for_template(player):
        return dict(
            treatment_earnings = player.participant.vars['treatment_earnings'],
            bc_earnings = player.participant.vars['bc_earnings'],
            risk_earnings = player.participant.vars['risk_earnings'],
            total_earnings = player.participant.vars['treatment_earnings']+player.participant.vars['bc_earnings']+player.participant.vars['risk_earnings'] + int(player.session.config['participation_fee']),
            show_up_fee = int(player.session.config['participation_fee']), #C.SHOW_UP_FEE,
            code = (player.participant.label)
            )
#-----------------------------------------------------------------------------------


#-----------------------------------------------------------------------------------
# PAGE SEQUENCE:
page_sequence = [
                # final results
                Survey,
                FinalResults
]
#-----------------------------------------------------------------------------------