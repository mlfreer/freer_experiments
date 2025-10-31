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

    # QUIZ ANSWERS:
    QUIZ_ANSWERS = [2,3,0]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    consent = models.BooleanField()

    # variables for the quiz answers:
    q1 = models.IntegerField()
    q2 = models.IntegerField()
    q3 = models.IntegerField()
    # model to count the quiz attempts
    quiz_attempts = models.IntegerField(initial = 0)
    return_study = models.IntegerField(initial = 0)
    # Prolific rule: 3 fails => return the study
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
        return (player.consent==False) or (player.return_study == True)

class Instructions(Page):
    pass

class Quiz(Page):
    form_model = 'player'
    form_fields = ['q1','q2','q3']

    @staticmethod
    def is_displayed(player):
        return (player.round_number == 1) and (player.return_study == False)

    def error_message(player, value):
        if ((value['q1']!=C.QUIZ_ANSWERS[1]) or (value['q2']!=C.QUIZ_ANSWERS[3]) or (value['q3']!=C.QUIZ_ANSWERS[3])) and (player.return_study == 0):
            result = 'Wrong answer! Try again!'
            player.quiz_attempts = player.quiz_attempts + 1
            if player.quiz_attempts >= 2:
                player.return_study = 1
            return result

#-----------------------------------------------------------------------------

page_sequence = [ConsentForm,  
                ReturnStudy, 
                Instructions,
                Quiz,
                ReturnStudy]




