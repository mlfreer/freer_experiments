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
    QUIZ_ANSWERS = [1,3,3]


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
    @staticmethod
    def vars_for_template(player: Player):
        session = player.session
        participant = player.participant
        return dict(
            # Used in instr.html to avoid unsupported '+' expressions in templates
            example_sum=session.config['A_BAR'] + participant.x_draw
        )

class Quiz(Page):
    form_model = 'player'
    form_fields = ['q1','q2','q3']

    @staticmethod
    def is_displayed(player):
        return (player.round_number == 1) and (player.return_study == False)

    def error_message(player, value):
        if ((value['q1']!=C.QUIZ_ANSWERS[0]) or (value['q2']!=C.QUIZ_ANSWERS[1]) or (value['q3']!=C.QUIZ_ANSWERS[2])) and (player.return_study == 0):
            result = 'Wrong answer! Try again!'
            player.quiz_attempts = player.quiz_attempts + 1
            if player.quiz_attempts >= 2:
                player.return_study = 1
            return result

    @staticmethod
    def vars_for_template(player: Player):
        session = player.session
        participant = player.participant
        a_bar = session.config['A_BAR']
        return dict(
            # Used in Quiz.html to avoid unsupported '+' expressions in templates
            two_heads_sum=a_bar + a_bar,
            heads_tails_sum=a_bar + participant.x_draw + 2,
            example_sum=session.config['A_BAR'] + participant.x_draw
        )

#-----------------------------------------------------------------------------

page_sequence = [ConsentForm,  
                ReturnStudy, 
                Instructions,
                Quiz,
                ReturnStudy]




