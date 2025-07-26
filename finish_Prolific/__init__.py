from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'finish_Prolific'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1




class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # prolific ID:
    ProlificID = models.StringField()


# PAGES
class ProlificID(Page):
    form_model = 'player'
    form_fields = ['ProlificID']
#    template_name = '_static/templates/ProlificID.html'
    def is_displayed(player):
        return player.subsession.round_number == C.NUM_ROUNDS

 

class Results(Page):
    def is_displayed(player):
        return player.subsession.round_number == C.NUM_ROUNDS
#    template_name = '_static/templates/Delegation_Results.html'

    @staticmethod
    def vars_for_template(player):
        return dict(
            showup = player.session.config['participation_fee'],
            payment = player.participant.payoff #player.payoff #+ player.session.config['participation_fee']
            )



page_sequence = [#ProlificID,
                Results]
