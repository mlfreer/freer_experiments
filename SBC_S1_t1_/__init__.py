import os
import random
import time

import pandas as pd
from otree.api import *

doc = """
Your app description
"""


# -----------------------------------------------------------------------------
# MODELS
class C(BaseConstants):
    NAME_IN_URL = "SBC_S1_t1_"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = (
        16  # setting the full length to ensure that data contains all necesasry info.
    )

    ENDOWMENT = cu(14)
    # TREATMENT ORDER:
    # 0 = static, buy at t=1
    # 1 = static, buy at t=2
    # 2 = dynamic, option
    # 3 = dynamic, refund
    #    PRICES_T1  = [[ 0 for i in range(15) ] for j in range(4)]
    PRICES_T1 = [
        [0 for i in range(16)] for j in range(4)
    ]  # changing the parameters to the 11 period setup
    # outside is for treatment: 0 to 3
    PRICES_T1[0] = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 4.5, 7.5, 8.5, 9.5, 13.5]
    PRICES_T1[2] = [8, 0, 0, 10, 2, 2, 4, 1, 1, 2, 3, 10, 6, 10, 4, 4]
    PRICES_T1[3] = [8, 12, 10, 10, 12, 10, 10, 9, 10, 9, 10, 12, 12, 14, 14, 6]
    # PRICES_T1[0] = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 8, 9, 11, 12]
    # PRICES_T1[2] = [8, 0, 0, 10, 1, 2, 1, 2, 3, 2, 3, 4, 7, 8, 9]
    # PRICES_T1[3] = [8, 12, 10, 10, 11, 12, 9, 10, 11, 8, 9, 10, 8, 9, 10]

    # PRICES_T2 = [[0 for i in range(15) ] for j in range(4)]
    PRICES_T2 = [[0 for i in range(16)] for j in range(4)]
    PRICES_T2[1] = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 4.5, 7.5, 8.5, 9.5, 13.5]
    PRICES_T2[2] = [0, 12, 10, 0, 10, 8, 6, 8, 9, 7, 7, 2, 6, 4, 10, 2]
    PRICES_T2[3] = [0, 12, 10, 0, 10, 8, 6, 8, 9, 7, 7, 2, 6, 4, 10, 2]
    # PRICES_T1[1] = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 8, 9, 11, 12]
    # PRICES_T2[2] = [0, 12, 10, 0, 10, 10, 8, 8, 8, 6, 6, 6, 1, 1, 1]
    # PRICES_T2[3] = [0, 12, 10, 0, 10, 10, 8, 8, 8, 6, 6, 6, 1, 1, 1]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    x = models.CurrencyField()
    # initial purchase variable.
    purchase = models.BooleanField(
        choices=[[True, "Yes"], [False, "No"]],
        widget=widgets.RadioSelectHorizontal,
        label="",
    )  # , label='Do you want to purchase this lottery ticket?', )

    # we start by introducing the revised purchase to every period.
    revised_purchase = models.BooleanField(
        choices=[[True, "Yes"], [False, "No"]],
        widget=widgets.RadioSelectHorizontal,
        label="",
    )  # , label='Do you want to purchase this lottery ticket?', )

    # to be converted to floats
    price_t1 = models.FloatField()
    price_t2 = models.FloatField()

    selected_round = models.IntegerField()
    random_draw_1 = models.IntegerField()
    random_draw_2 = models.IntegerField()
    treatment = models.IntegerField()

    # survey questions:
    pilot_comments = models.StringField()
    strategy = models.StringField()
    others_strategy = models.StringField()

    # time variables:
    decision_start = models.FloatField(blank=True)
    decision_rt = models.FloatField(blank=True)

    revision_start = models.FloatField(blank=True)
    revision_rt = models.FloatField(blank=True)

    comments_start = models.FloatField(blank=True)
    comments_rt = models.FloatField(blank=True)

# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# FUNCTIONS:
def draw_order(player: Player):
    session = player.session
    subsession = player.subsession
    participant = player.participant
    if (subsession.round_number == 1) or (participant.treatment == 1):
        import random

        indexes = list(range(len(C.PRICES_T1[participant.treatment])))
        random.shuffle(indexes)

        pricelist_t1 = list([C.PRICES_T1[participant.treatment][j] for j in indexes])
        pricelist_t2 = list([C.PRICES_T2[participant.treatment][j] for j in indexes])
        participant.price_order_t1 = pricelist_t1
        participant.price_order_t2 = pricelist_t2
        participant.indexes = indexes

        random_draw_1 = random.randint(0, 1)
        participant.random_draw_1 = random_draw_1

        random_draw_2 = random.randint(0, 1)
        participant.random_draw_2 = random_draw_2


# def save_to_csv(data_dict, filename="output.csv"):
# Convert dict to DataFrame (1 row)
#    df_new = pd.DataFrame([data_dict])
#
#    # If file exists, append without header
#    if os.path.exists(filename):
#        df_new.to_csv(filename, mode="a", index=False, header=False)
#    else:
#        df_new.to_csv(filename, mode="w", index=False, header=True)


# CREATING CUSTOM EXPORT:
def custom_export(players):
    # Header row
    yield [
        "participant.label",
        "participant.treatment",
        "participant.x_draw",
        "round_number",
        "price_t1",
        "price_t2",
        "random_draw_1",
        "random_draw_2",
        "revised_purchase",
        "purchase",
        "index",
    ]

    # One row per round per participant
    seen = set()  # avoid duplicate participants (since players has one per round)
    for player in players:
        participant = player.participant
        label = participant.label

        # Only process each participant once (last round player is fine)
        if label in seen:
            continue
        seen.add(label)

        rounds = participant.vars.get("rounds", [])
        for r in rounds:
            yield [
                label,
                participant.treatment,
                participant.x_draw,
                r.get("round_number", ""),
                r.get("price_t1", ""),
                r.get("price_t2", ""),
                r.get("random_draw_1", ""),
                r.get("random_draw_2", ""),
                r.get("revised_purchase", ""),  # blank for treatment 1
                r.get("purchase", ""),
                r.get("index", ""),
            ]


# -----------------------------------------------------------------------------
# PAGES
class ExperimentStarts(Page):
    form_model = "player"

    @staticmethod
    def is_displayed(player: Player):
        print(f"DEBUG ExperimentStarts round={player.round_number}")
        session = player.session
        subsession = player.subsession
        participant = player.participant
        if subsession.round_number == 1:
            player.x = participant.x_draw
            draw_order(player)
        # no choices for static, buy at t=2 treatment at this stage
        return player.round_number == 1

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
        )


class Decision(Page):
    form_model = "player"
    form_fields = ["purchase"]

    @staticmethod
    def is_displayed(player: Player):
        session = player.session
        subsession = player.subsession
        participant = player.participant
        player.price_t1 = participant.price_order_t1[subsession.round_number - 1]
        player.price_t2 = participant.price_order_t2[subsession.round_number - 1]
        player.x = participant.x_draw
        if player.participant.treatment == 1:
            # for the S2 treatment block the purchase as true.
            player.purchase = True
            player.revised_purchase = player.purchase
            return False
        else:
            return True

    @staticmethod
    def before_next_page(player, timeout_happened):
        if player.decision_start:
            player.decision_rt = time.time() - player.decision_start

        # generate the random draws in the first stage of the experiment:
        player.random_draw_1 = int(player.participant.random_draw_1)
        player.random_draw_2 = int(player.participant.random_draw_2)

        player.revised_purchase = player.purchase

        index = player.participant.indexes[player.subsession.round_number - 1]

    #        save_to_csv({
    #            "participant.label": player.participant.label,
    #            "participant.x_draw": player.participant.x_draw,
    #            "participant.treatment": player.participant.treatment,
    #            "player.price_t1": (player.price_t1),
    # "player.price_t2": (player.price_t2),
    #            "participant.indexes": index,
    # "player.random_draw_1": player.random_draw_1,
    # "player.random_draw_2": player.random_draw_2,
    #            "player.purchase": player.purchase,
    #            "player.revised_purchase": player.revised_purchase,
    #                # add other variables
    #        })

    @staticmethod
    def vars_for_template(player: Player):
        if player.field_maybe_none("decision_start") is None:
            player.decision_start = time.time()

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


# what should we record for the second stage?
class Results(Page):
    timeout_seconds = 10  # Timeout after 10 seconds

    @staticmethod
    def is_displayed(player: Player):
        subsession = player.subsession
        return subsession.round_number == C.NUM_ROUNDS

    @staticmethod
    @staticmethod
    def before_next_page(player, timeout_happened):
        if player.participant.treatment == 1:
            rounds = []
            for r in range(1, C.NUM_ROUNDS + 1):
                p = player.in_round(r)
                rounds.append(
                    {
                        "round_number": r,
                        "price_t1": p.price_t1,
                        "price_t2": p.price_t2,
                        "random_draw_1": int(player.participant.random_draw_1),
                        "random_draw_2": int(player.participant.random_draw_2),
                        #                    'revised_purchase': p.revised_purchase,
                        "index": player.participant.indexes[r - 1],
                    }
                )
        else:
            rounds = []
            for r in range(1, C.NUM_ROUNDS + 1):
                p = player.in_round(r)
                rounds.append(
                    {
                        "round_number": r,
                        "price_t1": p.price_t1,
                        "price_t2": p.price_t2,
                        "random_draw_1": int(player.participant.random_draw_1),
                        "random_draw_2": int(player.participant.random_draw_2),
                        "revised_purchase": p.revised_purchase,
                        "purchase": p.purchase,
                        "index": player.participant.indexes[r - 1],
                    }
                )

        player.participant.vars["rounds"] = rounds
        print(f"rounds saved (t=1): label={player.participant.label}, n={len(rounds)}")


# -----------------------------------------------------------------------------


# REVISION PAGE
class RevisionPage(Page):
    form_model = "player"

    @staticmethod
    def is_displayed(player: Player):
        return (player.round_number == C.NUM_ROUNDS) and (
            player.participant.treatment != 1
        )

    @staticmethod
    def live_method(player: Player, data: dict):
        round_num = data["round"]  # which round's decision is being revised
        revised = data["revised_purchase"]  # the new True/False value
        player.in_round(
            round_num
        ).revised_purchase = revised  # writes to that round's player object

    @staticmethod
    def vars_for_template(player: Player):
        if player.field_maybe_none("revision_start") is None:
            player.revision_start = time.time()

        past = []
        for r in range(1, C.NUM_ROUNDS + 1):
            p = player.in_round(r)
            past.append(
                dict(
                    round=r,
                    price_t1=p.price_t1,
                    price_t2=p.price_t2,
                    purchase=p.purchase,
                    revised_purchase=p.revised_purchase,
                    payment_prob=p.session.config["selected_for_payment"],
                    overwrite_decision=p.session.config["overwrite_decision"],
                    implement_decision=100 - p.session.config["overwrite_decision"],
                )
            )
        return dict(past_decisions=past)

    @staticmethod
    def before_next_page(player, timeout_happened):
        if player.revision_start:
            player.revision_rt = time.time() - player.revision_start



# -----------------------------------------------------------------------------
# Final completion page
class CompletionPage(Page):
    #    timeout_seconds = 60  # 1 minute to read the message

    @staticmethod
    def is_displayed(player: Player):
        subsession = player.subsession
        return subsession.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):

        participant = player.participant
        session = player.session

        return dict(
            completion_url=session.config["completion_url"],
        )


# -----------------------------------------------------------------------------
class Comments(Page):
    form_model = "player"
    form_fields = ["pilot_comments", "strategy", "others_strategy"]

    @staticmethod
    def is_displayed(player: Player):
        subsession = player.subsession
        return subsession.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        if player.field_maybe_none("comments_start") is None:
            player.comments_start = time.time()

    @staticmethod
    def before_next_page(player, timeout_happened):
        if player.comments_start:
            player.comments_rt = time.time() - player.comments_start


# ORDER
page_sequence = [
    ExperimentStarts,
    Decision,
    RevisionPage,
    Comments,
    Results,
    CompletionPage,
]
# -----------------------------------------------------------------------------
