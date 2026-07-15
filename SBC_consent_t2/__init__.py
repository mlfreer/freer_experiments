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

    # errors for the quiz
    q1_error = models.StringField(initial="", blank=True)
    q2_error = models.StringField(initial="", blank=True)
    q3_error = models.StringField(initial="", blank=True)

    # recording the lagged values
    q1_last = models.IntegerField(initial=None, blank=True)
    q2_last = models.IntegerField(initial=None, blank=True)
    q3_last = models.IntegerField(initial=None, blank=True)

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


# def retrieve_data(player):
#    import os

#    import pandas as pd

# Use absolute path to find output.csv in project root
# root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# csv_path = os.path.join(root_dir, 'output.csv')

#    try:
#        df = pd.read_csv("./output.csv", on_bad_lines="skip")
#    except TypeError:
#        # For older pandas versions that don't support on_bad_lines
#        df = pd.read_csv("./output.csv", error_bad_lines=False, warn_bad_lines=True)

# Find the matching row for this participant
#    print(df)
#    row = df.loc[df["participant.label"] == (player.participant.label)].iloc[0]

# Set participant variables from the data
#    player.participant.x_draw = int(row["participant.x_draw"])
##    player.participant.treatment = int(row["participant.treatment"])
#    player.participant.random_draw_1 = int(row["player.random_draw_1"])
#    player.participant.random_draw_2 = int(row["player.random_draw_2"])


STAGE_1_ROOMS = {
    "Prolific_Study_S1",
    "Prolific_Study_S2",
    "Prolific_Study_D1",
    "Prolific_Study_D2",
}


def get_room_name(session):
    """Safely retrieve room name via oTree's internal RoomToSession relation."""
    try:
        links = session.otree_RoomToSession
        if links:
            return links[0].room_name
    except Exception:
        pass
    return None


STAGE_1_ROOMS = {"Prolific_Study_S1", "Prolific_Study_D1"}


def get_room_name(session):
    """Safely retrieve room name via oTree's internal RoomToSession relation."""
    try:
        links = session.otree_RoomToSession
        if links:
            return links[0].room_name
    except Exception:
        pass
    return None


# ----------------------------------------------------------------------------------------------
def retrieve_data(player):
    label = player.participant.label
    if not label:
        print(f"retrieve_data: no label, skipping")
        return

    # Already retrieved — skip
    if player.participant.vars.get("x_draw") is not None:
        print(f"retrieve_data: already set for label={label}, skipping")
        return

    Participant = player.participant.__class__

    past = [
        pp
        for pp in Participant.objects_filter(label=label)
        if pp.session.id != player.participant.session.id
    ]

    if not past:
        print(f"retrieve_data: no past sessions found for label={label}")
        return

    source = max(past, key=lambda pp: pp.session.id)
    source_vars = source.vars

    print(
        f"retrieve_data: label={label}, source session={source.session.id}, "
        f"keys={list(source_vars.keys())}"
    )

    player.participant.x_draw = source_vars.get("x_draw")
    player.participant.treatment = source_vars.get("treatment")
    player.participant.random_draw_1 = source_vars.get("random_draw_1")
    player.participant.random_draw_2 = source_vars.get("random_draw_2")

    if player.participant.x_draw is None:
        print(
            f"retrieve_data: WARNING x_draw missing. Keys: {list(source_vars.keys())}"
        )


# ----------------------------------------------------------------------------------------------


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
        # Always attempt to retrieve — idempotent if already set
        if participant.vars.get("x_draw") is None:
            retrieve_data(player)

        return dict(
            # Used in instr.html to avoid unsupported '+' expressions in templates
            example_sum=session.config["A_BAR"] + participant.x_draw,
            two_heads_sum=2 * session.config["A_BAR"],
            payment_prob=session.config["selected_for_payment"],
            overwrite_decision=session.config["overwrite_decision"],
            implement_decision=100 - session.config["overwrite_decision"],
        )


class Quiz(Page):
    form_model = "player"
    form_fields = ["q1", "q2", "q3"]

    @staticmethod
    def is_displayed(player):
        return (player.round_number == 1) and (player.return_study == False)

    @staticmethod
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


page_sequence = [
    #    ConsentForm,
    ReturnStudy,
    Instructions,
    Quiz,
    ReturnStudy,
]
