import random
import time
from otree.api import *

doc = """
STATIC MECHANISM 1
t=2 interface
"""


class C(BaseConstants):
    NAME_IN_URL = "SBC_S1_t2_"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 16

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
    # prolificID = models.StringField()
    # test variabbles:
    q1 = models.StringField(label="Question 1")
    q2 = models.StringField(label="Question 2")
    q3 = models.StringField(label="Question 2")

    purchase_t1 = models.BooleanField(default=False)
    purchase_t2 = models.BooleanField(default=False)

    revised_purchase_t2 = models.BooleanField(default=False)

    # to be converted to floats:
    price_t1 = models.FloatField()
    price_t2 = models.FloatField()
    earnings = models.FloatField()

    selected_round = models.IntegerField()
    random_draw_1 = models.IntegerField()
    random_draw_2 = models.IntegerField()
    treatment = models.StringField()

    payoff_calculated = models.BooleanField(default=False)
    random_draws_generated = models.BooleanField(default=False)

    # selected for payment:
    selected_for_payment = models.BooleanField(default=True)
    decision_overwritten = models.BooleanField(default=False)

    # survey questions:
    pilot_comments = models.StringField()
    strategy = models.StringField()
    others_strategy = models.StringField()

    # preference parameters:
    risk = models.IntegerField()
    time = models.IntegerField()
    endowment = models.CurrencyField()
    complexity = models.IntegerField()

    numeracy1 = models.IntegerField()
    numeracy2 = models.IntegerField()

    # time variables:
    decision_start = models.FloatField(blank=True)
    decision_rt = models.FloatField(blank=True)

    revision_start = models.FloatField(blank=True)
    revision_rt = models.FloatField(blank=True)

    comments_start = models.FloatField(blank=True)
    comments_rt = models.FloatField(blank=True)


# --------------------------------------------------------
# FUNCTIONS:
def draw_order(player: Player):
    session = player.session
    subsession = player.subsession
    participant = player.participant
    if (subsession.round_number == 1) or (participant.treatment == 0):
        import random

        indexes = list(range(len(C.PRICES_T1[participant.treatment])))
        random.shuffle(indexes)

        pricelist_t1 = list([C.PRICES_T1[participant.treatment][j] for j in indexes])
        pricelist_t2 = list([C.PRICES_T2[participant.treatment][j] for j in indexes])
        participant.price_order_t1 = pricelist_t1
        participant.price_order_t2 = pricelist_t2
        participant.indexes = indexes


def retrieve_data(player):
    participant = player.participant
    label = participant.label
    if not label:
        print(f"retrieve_data: no label, skipping")
        return

    if participant.treatment != 1:
        subsession = player.subsession

        player.price_t1 = participant.price_order_t1[subsession.round_number - 1]
        player.price_t2 = participant.price_order_t2[subsession.round_number - 1]
        index = participant.indexes[subsession.round_number - 1]

        # Skip if already retrieved for this round
        if player.field_maybe_none("random_draw_1") is not None:
            return

        Participant = participant.__class__
        past = [
            pp
            for pp in Participant.objects_filter(label=label)
            if pp.session.id != participant.session.id
        ]

        if not past:
            print(f"retrieve_data: no past session for label={label}")
            return

        source = max(past, key=lambda pp: pp.session.id)
        rounds = source.vars.get("rounds", [])

        print(
            f"retrieve_data: label={label}, round={subsession.round_number}, "
            f"source session={source.session.id}, rounds={len(rounds)}"
        )

        matched = next(
            (
                r
                for r in rounds
                if r["price_t1"] == player.price_t1
                and r["price_t2"] == player.price_t2
                and r["index"] == index
            ),
            None,
        )

        if matched is None:
            print(
                f"retrieve_data: no match for label={label}, "
                f"price_t1={player.price_t1}, price_t2={player.price_t2}, index={index}"
            )
            print(f"retrieve_data: available rounds={rounds}")
            return

        player.random_draw_1 = int(matched["random_draw_1"])
        player.random_draw_2 = int(matched["random_draw_2"])
        player.purchase_t1 = bool(matched["revised_purchase"])

    else:
        # treatment 1: no t=1 decision, draws carried on participant directly
        if player.field_maybe_none("random_draw_1") is not None:
            return
        player.random_draw_1 = int(participant.random_draw_1)
        player.random_draw_2 = int(participant.random_draw_2)


def select_random_round(player: Player):
    import random

    participant = player.participant
    subsession = player.subsession
    session = player.session

    # choosing the payment round
    selected_round = random.randint(1, C.NUM_ROUNDS)
    player.selected_round = selected_round


def compute_payoff(player: Player):
    if player.field_maybe_none("payoff_calculated"):
        return

    payment_prob = player.session.config["selected_for_payment"]
    overwrite_decision = player.session.config["overwrite_decision"]

    participant = player.participant
    subsession = player.subsession
    session = player.session

    # Initialize earnings to endowment in case no round matches
    endowment = int(C.ENDOWMENT)
    player.earnings = endowment

    # print(f"Computing payoff for player, selected_round: {player.selected_round}")

    for p in player.in_all_rounds():
        retrieve_data(p)
        # print(f"Checking round {p.round_number} against selected {player.selected_round} , purchase_t1: {p.purchase_t1}, purchase_t2: {p.purchase_t2}")
        if p.round_number == player.selected_round:
            # determining the payoff
            x_draw = participant.x_draw
            a_bar = session.config["A_BAR"]
            price_t1 = p.price_t1
            price_t2 = p.price_t2

            # determining if the ticket is won at t=1
            print(f"Round matched! random_draw_1: {p.random_draw_1}")
            won_t1 = p.random_draw_1 == 1
            won_t2 = p.random_draw_2 == 1

            # checking whether the decision is overridden:
            purchased_t1 = p.purchase_t1
            random_draw = random.randint(0, 100)
            if (random_draw < overwrite_decision) and (participant.treatment > 1):
                purchased_t1 = True
                player.decision_overwritten = True

            if participant.treatment == 0:  # static, buy at t=1
                if purchased_t1:
                    player.earnings = (
                        endowment
                        - price_t1
                        + a_bar * won_t1
                        + x_draw * (1 - won_t1)
                        + a_bar * won_t2
                    )
                else:
                    player.earnings = endowment
                print(
                    f"Treatment 0 - purchase_t1: {p.purchase_t1}, earnings: {player.earnings}"
                )

            elif participant.treatment == 1:  # static, buy at t=2
                if p.revised_purchase_t2:
                    player.earnings = (
                        endowment
                        - price_t2
                        + a_bar * won_t1
                        + x_draw * (1 - won_t1)
                        + a_bar * won_t2
                    )
                else:
                    player.earnings = endowment
            elif participant.treatment == 2:  # dynamic, option
                if purchased_t1:
                    if p.revised_purchase_t2:
                        player.earnings = (
                            endowment
                            - price_t1
                            - price_t2
                            + a_bar * won_t1
                            + x_draw * (1 - won_t1)
                            + a_bar * won_t2
                        )
                    else:
                        player.earnings = endowment - price_t1
                else:
                    player.earnings = endowment
            elif participant.treatment == 3:  # dynamic, refund
                if purchased_t1:
                    if p.revised_purchase_t2 == 0:
                        player.earnings = (
                            endowment
                            - price_t1
                            + a_bar * won_t1
                            + x_draw * (1 - won_t1)
                            + a_bar * won_t2
                        )
                    else:
                        player.earnings = endowment - price_t1 + price_t2
                else:
                    player.earnings = endowment

            # checking whether the player is to get paid:
            random_draw = random.randint(0, 100)
            print(random_draw, payment_prob)
            if (
                random_draw >= payment_prob
            ):  # if the prob is above the threshold we nulify it
                player.earnings = 0
                player.selected_for_payment = False

            # print(f"Final earnings set to: {player.earnings}")
            player.payoff_calculated = (
                True  # marking the fact that payoff is calculated
            )
            break  # Found the selected round, no need to continue


def custom_export(players):
    yield [
        "participant.label",
        "participant.treatment",
        "participant.x_draw",
        "round_number",
        "price_t1",
        "price_t2",
        "random_draw_1",
        "random_draw_2",
        "purchase_t1",
        "purchase_t2",
        "revised_purchase_t2",
        "earnings",
        "selected_round",
        "selected_for_payment",
        "decision_overwritten",
        "payoff_calculated",
    ]

    seen = set()
    for player in players:
        participant = player.participant
        label = participant.label

        # Only process each participant once using the last round player
        if label in seen or player.round_number != C.NUM_ROUNDS:
            continue
        seen.add(label)

        for r in range(1, C.NUM_ROUNDS + 1):
            p = player.in_round(r)
            yield [
                label,
                participant.treatment,
                participant.x_draw,
                r,
                p.field_maybe_none("price_t1"),
                p.field_maybe_none("price_t2"),
                p.field_maybe_none("random_draw_1"),
                p.field_maybe_none("random_draw_2"),
                p.field_maybe_none("purchase_t1"),
                p.field_maybe_none("purchase_t2"),
                p.field_maybe_none("revised_purchase_t2"),
                p.field_maybe_none("earnings"),
                p.field_maybe_none("selected_round"),
                p.field_maybe_none("selected_for_payment"),
                p.field_maybe_none("decision_overwritten"),
                p.field_maybe_none("payoff_calculated"),
            ]


# --------------------------------------------------------
# PAGES


# TEST PAGE WITH PROLIFIC ID
class ExperimentStarts(Page):
    @staticmethod
    def is_displayed(player):
        if player.participant.treatment != 0:
            return player.subsession.round_number == 1
        else:
            return player.subsession.round_number == C.NUM_ROUNDS

    @staticmethod
    def before_next_page(player, timeout_happened):
        # comptuing payoff at the start of the experiment if the treatment is static, buy at t=1
        if player.participant.treatment == 0:
            retrieve_data(player)
            select_random_round(player)
            compute_payoff(player)

    @staticmethod
    def vars_for_template(player):
        participant = player.participant
        session = player.session
        # Load data from stage t1 before drawing any new order.
        draw_order(player)
        retrieve_data(player)

        # Calculate example_sum for instructions
        a_bar = session.config["A_BAR"]
        x_draw = participant.x_draw
        example_sum = x_draw + a_bar

        result = "heads" if player.random_draw_1 == 1 else "tails"

        return dict(
            treatment=participant.treatment,
            x_draw=x_draw,
            example_sum=example_sum,
            two_heads_sum=2 * a_bar,
            coin_result=result,
            payment_prob=session.config["selected_for_payment"],
            overwrite_decision=session.config["overwrite_decision"],
            implement_decision=100 - session.config["overwrite_decision"],
        )


# PAGE WITH MULTIPLE STEPS (BACK AND FORTH BUTTON
class Decision(Page):
    form_model = "player"
    form_fields = ["purchase_t2"]

    @staticmethod
    def is_displayed(player: Player):
        session = player.session
        subsession = player.subsession
        participant = player.participant
        if participant.treatment != 0:
            player.price_t1 = participant.price_order_t1[subsession.round_number - 1]
            player.price_t2 = participant.price_order_t2[subsession.round_number - 1]
        x_draw = participant.x_draw  # temp variable for x_draw
        return participant.treatment != 0

    @staticmethod
    def vars_for_template(player: Player):
        if player.field_maybe_none("decision_start") is None:
            player.decision_start = time.time()

        # recovering the data:
        retrieve_data(player)

        # Calculate example_sum for instructions
        participant = player.participant
        session = player.session
        a_bar = session.config["A_BAR"]
        x_draw = participant.x_draw
        example_sum = x_draw + a_bar

        return dict(
            price_t1=player.price_t1,
            price_t2=player.price_t2,
            x_draw=x_draw,
            example_sum=example_sum,
            two_heads_sum=2 * a_bar,
            payment_prob=session.config["selected_for_payment"],
            overwrite_decision=session.config["overwrite_decision"],
            implement_decision=100 - session.config["overwrite_decision"],
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.revised_purchase_t2 = player.purchase_t2
        if player.decision_start:
            player.decision_rt = time.time() - player.decision_start

        # temporary removing to compute the payoffs after the revision page


# if player.subsession.round_number == C.NUM_ROUNDS:
# select_random_round(player)
# compute_payoff(player)


# REVISION PAGE
class RevisionPage(Page):
    form_model = "player"

    @staticmethod
    def is_displayed(player: Player):
        return (player.subsession.round_number == C.NUM_ROUNDS) and (
            player.participant.treatment != 0
        )

    @staticmethod
    def live_method(player: Player, data: dict):
        round_num = data["round"]  # which round's decision is being revised
        revised = data["revised_purchase"]  # the new True/False value
        player.in_round(
            round_num
        ).revised_purchase_t2 = revised  # writes to that round's player object

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
                    purchase_t2=p.purchase_t2,
                    revised_purchase_t2=p.revised_purchase_t2,
                    payment_prob=p.session.config["selected_for_payment"],
                    overwrite_decision=p.session.config["overwrite_decision"],
                    implement_decision=100 - p.session.config["overwrite_decision"],
                )
            )
        return dict(past_decisions=past)

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.revision_start:
            player.revision_rt = time.time() - player.revision_start
        if player.subsession.round_number == C.NUM_ROUNDS:
            select_random_round(player)
            compute_payoff(player)


class Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.subsession.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        participant = player.participant
        session = player.session

        selected_player = player.in_round(player.selected_round)
        retrieve_data(selected_player)
        compute_payoff(player)

        # recording the payoff in the end:
        player.payoff = player.earnings

        return dict(
            selected_round=player.selected_round,
            payoff=player.field_maybe_none("earnings"),
            price_t1=selected_player.price_t1,
            price_t2=selected_player.price_t2,
            purchase_t1=selected_player.field_maybe_none("purchase_t1"),
            purchase_t2=selected_player.field_maybe_none("revised_purchase_t2"),
            random_draw_1=selected_player.field_maybe_none("random_draw_1"),
            random_draw_2=selected_player.field_maybe_none("random_draw_2"),
            x_draw=participant.x_draw,
            a_bar=session.config["A_BAR"],
            treatment=participant.treatment,
            payment_prob=session.config["selected_for_payment"],
            overwrite_decision=session.config["overwrite_decision"],
            implement_decision=100 - session.config["overwrite_decision"],
            completion_url=session.config["completion_url"],
        )


# ---------------------------------------------------------------------
# SURVEY
class Survey(Page):
    form_model = "player"
    form_fields = [
        "pilot_comments",
        "strategy",
        "others_strategy",
        "risk",
        "time",
        "complexity",
        "endowment",
        "numeracy1",
        "numeracy2",
    ]

    @staticmethod
    def is_displayed(player: Player):
        return player.subsession.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        if player.field_maybe_none("comments_start") is None:
            player.comments_start = time.time()
        return dict(likert_range=range(11))

    @staticmethod
    def before_next_page(player, timeout_happened):
        if player.comments_start:
            player.comments_rt = time.time() - player.comments_start

page_sequence = [ExperimentStarts, Decision, RevisionPage, Survey, Results]
