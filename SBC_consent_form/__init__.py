import random
import time

from otree.api import *

doc = """
Your app description
"""


# -----------------------------------------------------------------------------
# CLASSES
class C(BaseConstants):
    NAME_IN_URL = "SBC_consent_form"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    ENDOWMENT = cu(14)

    # QUIZ ANSWERS:
    QUIZ_ANSWERS = [1, 3, 3]

    # INTEGERS TO INPUT IN THE EXAMPLE PAGE:
    EXAMPLE_ANSWERS = [ENDOWMENT, 18, 12]


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

    # errors for the quiz
    q1_error = models.StringField(initial="", blank=True)
    q2_error = models.StringField(initial="", blank=True)
    q3_error = models.StringField(initial="", blank=True)

    # recording the lagged values
    q1_last = models.IntegerField(initial=None, blank=True)
    q2_last = models.IntegerField(initial=None, blank=True)
    q3_last = models.IntegerField(initial=None, blank=True)

    # variables for the example page:
    e1 = models.IntegerField()
    e2 = models.IntegerField()
    e3 = models.IntegerField()

    # errors for example
    e1_error = models.StringField(initial="", blank=True)
    e2_error = models.StringField(initial="", blank=True)
    e3_error = models.StringField(initial="", blank=True)

    e1_last = models.IntegerField(initial=None, blank=True)
    e2_last = models.IntegerField(initial=None, blank=True)
    e3_last = models.IntegerField(initial=None, blank=True)

    # model to count the quiz attempts
    quiz_attempts = models.IntegerField(initial=0)
    return_study = models.IntegerField(initial=0)
    # Prolific rule: 3 fails => return the study

    # counting the number of mistakes in the example:
    example_attempts = models.IntegerField(initial=0)

    # time variables:
    instructions_start = models.FloatField(blank=True)
    instructions_rt = models.FloatField(blank=True)

    example_start = models.FloatField(blank=True)
    example_rt = models.FloatField(blank=True)

    quiz_start = models.FloatField(blank=True)
    quiz_rt = models.FloatField(blank=True)


# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# FUNCTIONS:


def draw_x(player: Player):
    session = player.session
    participant = player.participant
    participant.x_draw = round(random.randint(0, session.config["A_BAR"]), 0)
    participant.treatment = session.config["treatment"]


def creating_session(subsession):
    for p in subsession.get_players():
        draw_x(p)


# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# PAGES
class ConsentForm(Page):
    form_model = "player"
    form_fields = ["consent"]

    def before_next_page(player: Player, timeout_happened):
        draw_x(player)


class ReturnStudy(Page):
    template_name = "_static/global/ReturnStudy.html"

    def is_displayed(player: Player):
        return player.return_study == True


class Instructions(Page):
    @staticmethod
    def vars_for_template(player: Player):
        if player.field_maybe_none("instructions_start") is None:
            player.instructions_start = time.time()

        session = player.session
        participant = player.participant
        return dict(
            # Used in instr.html to avoid unsupported '+' expressions in templates
            two_heads_sum=session.config["A_BAR"] + session.config["A_BAR"],
            example_sum=session.config["A_BAR"] + participant.x_draw,
            payment_prob=session.config["selected_for_payment"],
            overwrite_decision=session.config["overwrite_decision"],
            implement_decision=100 - session.config["overwrite_decision"],
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.instructions_start:
            player.instructions_rt = time.time() - player.instructions_start

class Example(Page):
    form_model = "player"
    form_fields = ["e1", "e2", "e3"]

    @staticmethod
    def is_displayed(player):
        return (player.round_number == 1) and (player.return_study == False)

    @staticmethod
    def vars_for_template(player):

        if player.field_maybe_none("example_start") is None:
            player.example_start = time.time()


        session = player.session
        participant = player.participant

        e1_error = player.e1_error
        e2_error = player.e2_error
        e3_error = player.e3_error

        return dict(
            two_heads_sum=session.config["A_BAR"] + session.config["A_BAR"],
            example_sum=session.config["A_BAR"] + participant.x_draw,
            payment_prob=session.config["selected_for_payment"],
            overwrite_decision=session.config["overwrite_decision"],
            implement_decision=100 - session.config["overwrite_decision"],
            e1_error=e1_error,
            e2_error=e2_error,
            e3_error=e3_error,
            e1_last=player.field_maybe_none("e1_last"),
            e2_last=player.field_maybe_none("e2_last"),
            e3_last=player.field_maybe_none("e3_last"),
        )

    @staticmethod
    def error_message(player, values):
        errors = {}
        player.e1_last = values["e1"]
        player.e2_last = values["e2"]
        player.e3_last = values["e3"]

        # Force int comparison to be safe
        try:
            v1 = int(values["e1"])
        except (TypeError, ValueError):
            v1 = None
        try:
            v2 = int(values["e2"])
        except (TypeError, ValueError):
            v2 = None
        try:
            v3 = int(values["e3"])
        except (TypeError, ValueError):
            v3 = None

        if v1 != int(C.EXAMPLE_ANSWERS[0]):
            errors["e1"] = "Incorrect. Please check your calculation for Question 1."
        if v2 != int(C.EXAMPLE_ANSWERS[1]):
            errors["e2"] = "Incorrect. Please check your calculation for Question 2."
        if v3 != int(C.EXAMPLE_ANSWERS[2]):
            errors["e3"] = "Incorrect. Please check your calculation for Question 3."

        if errors:
            player.example_attempts += 1
            player.e1_error = errors.get("e1", "")
            player.e2_error = errors.get("e2", "")
            player.e3_error = errors.get("e3", "")
            return "error"
        else:
            player.e1_error = ""
            player.e2_error = ""
            player.e3_error = ""

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.example_start:
            player.example_rt = time.time() - player.example_start



class Quiz(Page):
    form_model = "player"
    form_fields = ["q1", "q2", "q3"]

    @staticmethod
    def is_displayed(player):
        return (player.round_number == 1) and (player.return_study == False)

    @staticmethod
    def vars_for_template(player: Player):

        if player.field_maybe_none("quiz_start") is None:
            player.quiz_start = time.time()

        session = player.session
        participant = player.participant
        a_bar = session.config["A_BAR"]
        return dict(
            # Used in Quiz.html to avoid unsupported '+' expressions in templates
            two_heads_sum=a_bar + a_bar,
            heads_tails_sum=a_bar + 14,
            example_sum=session.config["A_BAR"] + participant.x_draw,
            payment_prob=session.config["selected_for_payment"],
            overwrite_decision=session.config["overwrite_decision"],
            implement_decision=100 - session.config["overwrite_decision"],
            q1_error=player.q1_error,
            q2_error=player.q2_error,
            q3_error=player.q3_error,
            q1_last=player.field_maybe_none("q1_last"),
            q2_last=player.field_maybe_none("q2_last"),
            q3_last=player.field_maybe_none("q3_last"),
        )

    @staticmethod
    def error_message(player, values):
        errors = {}
        player.q1_last = int(values["q1"])
        print(player.q1_last)
        player.q2_last = int(values["q2"])
        player.q3_last = int(values["q3"])

        # Force int comparison to be safe
        try:
            v1 = int(values["q1"])
        except (TypeError, ValueError):
            v1 = None
        try:
            v2 = int(values["q2"])
        except (TypeError, ValueError):
            v2 = None
        try:
            v3 = int(values["q3"])
        except (TypeError, ValueError):
            v3 = None

        if v1 != int(C.QUIZ_ANSWERS[0]):
            errors["q1"] = "Incorrect. Please check your answer for Question 1."
        if v2 != int(C.QUIZ_ANSWERS[1]):
            errors["q2"] = "Incorrect. Please check your answer for Question 2."
        if v3 != int(C.QUIZ_ANSWERS[2]):
            errors["q3"] = "Incorrect. Please check your answer for Question 3."

        if errors:
            player.quiz_attempts = player.quiz_attempts + 1
            if player.quiz_attempts > 2:
                player.return_study = 1
            player.q1_error = errors.get("q1", "")
            player.q2_error = errors.get("q2", "")
            player.q3_error = errors.get("q3", "")
            return "Please correct the aswers"
        else:
            player.q1_error = ""
            player.q2_error = ""
            player.q3_error = ""

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.quiz_start:
            player.quiz_rt = time.time() - player.quiz_start


# -----------------------------------------------------------------------------

page_sequence = [
    #    ConsentForm,
    ReturnStudy,
    Instructions,
    Example,
    Quiz,
    ReturnStudy,
]
