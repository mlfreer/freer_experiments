from otree.api import *
import random

doc = """
Your app description
"""


#-----------------------------------------------------------------------------
# CLASSES
class C(BaseConstants):
    NAME_IN_URL = 'SBC_consent_form'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    ENDOWMENT = 15


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    consent = models.BooleanField()
#-----------------------------------------------------------------------------




#-----------------------------------------------------------------------------
# FUNCTIONS:
def draw_x(player: Player):
    session = player.session
    participant = player.participant
    participant.x_draw = round(random.randint(0, session.config['A_BAR']), 0)
    participant.treatment = session.config['treatment']


#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# PAGES
class ConsentForm(Page):
    form_model = 'player'
    form_fields = ['consent']

    def before_next_page(player: Player, timeout_happened):
        draw_x(player)

class ReturnStudy(Page):
    template_name = "_static/global/ReturnStudy.html"
    def is_displayed(player: Player):
        return player.consent==False

class Instructions(Page):
    pass

class Quiz(Page):
    pass
#-----------------------------------------------------------------------------

page_sequence = [ConsentForm,  
                ReturnStudy, 
                Instructions,
                Quiz]




