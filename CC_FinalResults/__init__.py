from otree.api import *
import random

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'CC_FinalResults'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    SHOW_UP_FEE = 5

    exchange_rate = .5


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    final_earnings = models.FloatField(default=0,max_digits=5, decimal_places=2)
    final_certificate = models.FloatField(default=0,max_digits=5, decimal_places=2)

    reasoning = models.StringField(required = False)
    wta = models.StringField(required = False)
    certificate = models.StringField(required = False)


#----------------------------------------
# PAGES

#----------------------------------------
class Survey(Page):
    form_model = 'player'
    form_fields = ['reasoning', 'wta', 'certificate']
#----------------------------------------


#----------------------------------------
class Results(Page):
    def vars_for_template(player):
        random_number = random.random()
        if random_number >= .5:
            player.final_earnings = player.participant.vars['T1_earnings']*C.exchange_rate
            player.final_certificate = player.participant.vars['T1_certificate']*C.exchange_rate
        else:
            player.final_earnings = player.participant.vars['T2_earnings']*C.exchange_rate
            player.final_certificate = player.participant.vars['T2_certificate']*C.exchange_rate

        if player.final_certificate>0:
            player.payoff = (player.final_earnings + player.final_certificate)
        else:
            player.payoff = player.final_earnings
        

        return dict(
            final_earnings = cu(player.final_earnings),
            final_certificate = cu(player.final_certificate),
            show_up_fee = cu(C.SHOW_UP_FEE),
            payoff = cu(player.payoff + C.SHOW_UP_FEE),
            code = player.participant.code
            )
#----------------------------------------



#----------------------------------------


page_sequence = [Survey,
                Results]
