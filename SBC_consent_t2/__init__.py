from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'SBC_consent_t2'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    # passing the endowment to instructions page
    ENDOWMENT = 15

    # QUIZ ANSWERS:
    QUIZ_ANSWERS = [1,0,3]


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
    # Prolific rule: 3 fails => return the studys


# FUNCTIONS:


def retrieve_data(player):
    import pandas as pd
    import os

    # Use absolute path to find output.csv in project root
    #root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    #csv_path = os.path.join(root_dir, 'output.csv')
    
    df = pd.read_csv('./output.csv')

    # Find the matching row for this participant
    print(df)
    row = df.loc[df['participant.label'] == (player.participant.label)].iloc[0]
    
    # Set participant variables from the data
    player.participant.x_draw = float(row['participant.x_draw'])
    player.participant.treatment = int(row['participant.treatment'])
    


# PAGES
class ConsentForm(Page):
    template_name = 'SBC_consent_t2/Consent_t2.html'
    form_model = 'player'
    form_fields = ['consent']

    def before_next_page(player: Player, timeout_happened):
        retrieve_data(player) # use the function that would retrieve the data.
    


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
    def vars_for_template(player: Player):
        session = player.session
        participant = player.participant
        return dict(
            two_heads_sum = 2*session.config['A_BAR'],
            heads_tails_sum = session.config['A_BAR'] + participant.x_draw + 2,
            example_sum=session.config['A_BAR'] + participant.x_draw
        )



page_sequence = [ConsentForm,  
                Instructions,
                Quiz]
