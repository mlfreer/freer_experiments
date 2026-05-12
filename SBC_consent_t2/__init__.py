from otree.api import *

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = "SBC_consent_t2"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    # passing the endowment to instructions page
    ENDOWMENT = cu(14)

    # QUIZ ANSWERS:
    QUIZ_ANSWERS = [1, 0, 3]

    # INTEGERS TO INPUT IN THE EXAMPLE PAGE:
    EXAMPLE_ANSWERS = [0, 0, 0]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # consent = models.BooleanField()

    # variables for the quiz answers:
    q1 = models.IntegerField()
    q2 = models.IntegerField()
    q3 = models.IntegerField()
    # model to count the quiz attempts
    quiz_attempts = models.IntegerField(initial=0)
    return_study = models.IntegerField(initial=0)
    # Prolific rule: 3 fails => return the studys

    # adding the counter for example_attempts
    example_attempts = models.IntegerField(initial=0)

    # variables for the example page:
    e1 = models.IntegerField()
    e2 = models.IntegerField()
    e3 = models.IntegerField()


# FUNCTIONS:


def retrieve_data(player):
    import os

    import pandas as pd

    # Use absolute path to find output.csv in project root
    # root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # csv_path = os.path.join(root_dir, 'output.csv')

    try:
        df = pd.read_csv("./output.csv", on_bad_lines="skip")
    except TypeError:
        # For older pandas versions that don't support on_bad_lines
        df = pd.read_csv("./output.csv", error_bad_lines=False, warn_bad_lines=True)

    # Find the matching row for this participant
    print(df)
    row = df.loc[df["participant.label"] == (player.participant.label)].iloc[0]

    # Set participant variables from the data
    player.participant.x_draw = int(row["participant.x_draw"])
    player.participant.treatment = int(row["participant.treatment"])
    player.participant.random_draw_1 = int(row["player.random_draw_1"])
    player.participant.random_draw_2 = int(row["player.random_draw_2"])


# PAGES
class ConsentForm(Page):
    template_name = "SBC_consent_t2/Consent_t2.html"
    form_model = "player"
    form_fields = ["consent"]

    def before_next_page(player: Player, timeout_happened):
        retrieve_data(player)  # use the function that would retrieve the data.


class ReturnStudy(Page):
    template_name = "_static/global/ReturnStudy.html"

    @staticmethod
    def is_displayed(player: Player):
        return player.return_study == True


class Instructions(Page):
    @staticmethod
    def vars_for_template(player: Player):
        session = player.session
        participant = player.participant

        # Only load from CSV once, the first time we hit this page
        # Safely check whether x_draw is already set
        try:
            _ = participant.x_draw
        except KeyError:
            # First time we are here for this participant: load from CSV
            retrieve_data(player)

        return dict(
            # Used in instr.html to avoid unsupported '+' expressions in templates
            example_sum=session.config["A_BAR"] + participant.x_draw,
            two_heads_sum=2 * session.config["A_BAR"],
            payment_prob=session.config["selected_for_payment"],
            overwrite_decision=session.config["overwrite_decision"],
            implement_decision=100 - session.config["overwrite_decision"],
        )


class Example(Page):
    form_model = "player"
    form_fields = ["e1", "e2", "e3"]

    @staticmethod
    def is_displayed(player):
        return (player.round_number == 1) and (player.return_study == False)

    def error_message(player, value):
        if (
            (value["e1"] != C.EXAMPLE_ANSWERS[0])
            or (value["e2"] != C.EXAMPLE_ANSWERS[1])
            or (value["e3"] != C.EXAMPLE_ANSWERS[2])
        ):
            player.example_attempts += 1
            return "Wrong answer! Please try again!"


class Quiz(Page):
    form_model = "player"
    form_fields = ["q1", "q2", "q3"]

    @staticmethod
    def is_displayed(player):
        return (player.round_number == 1) and (player.return_study == False)

    def error_message(player, value):
        if (
            (value["q1"] != C.QUIZ_ANSWERS[0])
            or (value["q2"] != C.QUIZ_ANSWERS[1])
            or (value["q3"] != C.QUIZ_ANSWERS[2])
        ) and (player.return_study == 0):
            result = "Wrong answer! Try again!"
            player.quiz_attempts = player.quiz_attempts + 1
            if player.quiz_attempts >= 2:
                player.return_study = 1
            return result

    def vars_for_template(player: Player):
        session = player.session
        participant = player.participant
        return dict(
            two_heads_sum=2 * session.config["A_BAR"],
            heads_tails_sum=session.config["A_BAR"] + 14,
            example_sum=session.config["A_BAR"] + participant.x_draw,
            payment_prob=session.config["selected_for_payment"],
            overwrite_decision=session.config["overwrite_decision"],
            implement_decision=100 - session.config["overwrite_decision"],
        )


page_sequence = [
    #    ConsentForm,
    ReturnStudy,
    #     Example,
    Instructions,
    Quiz,
    ReturnStudy,
]
