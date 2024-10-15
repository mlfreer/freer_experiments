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

    email = models.StringField(required = True)

    reasoning = models.StringField(required = False)
    wta = models.StringField(required = False)
#    certificate = models.StringField(required = False)
    
    gender = models.IntegerField(initial = -1)
    british = models.IntegerField(initial = -1)
    ethinicity = models.StringField()
    age = models.IntegerField(min=16, max=99)
    undergrad = models.IntegerField(initial=-1)
    gaming = models.IntegerField(initial = -1)
    socialmedia = models.IntegerField(initial=-1)
    siblings = models.IntegerField(initial=-1)
    cohabitants = models.IntegerField(initial=-1)


#----------------------------------------
# PAGES

#----------------------------------------
class Survey(Page):
    form_model = 'player'
    form_fields = ['reasoning','gender','age','british','undergrad','socialmedia','gaming','siblings','cohabitants']
#----------------------------------------

class FinalWaitPage(WaitPage):
    pass
#----------------------------------------
class Results(Page):
    form_model = 'player'
    form_fields = ['email']

    def vars_for_template(player):   
        player.final_earnings = player.participant.vars['T1_earnings']*C.exchange_rate
        player.payoff = player.final_earnings+C.SHOW_UP_FEE
        user_name = player.participant.vars['user_name']
        return dict(
            final_earnings = cu(player.final_earnings),
            show_up_fee = cu(C.SHOW_UP_FEE),
            payoff = cu(player.payoff),
            code = player.participant.code,
            user_name= user_name
            )
#----------------------------------------


#----------------------------------------
class FinalPage(Page):
    pass
#----------------------------------------


#----------------------------------------


page_sequence = [FinalWaitPage,
                Survey,
                Results,
                FinalPage]
