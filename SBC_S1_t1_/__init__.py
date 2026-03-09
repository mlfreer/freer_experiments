from otree.api import *
import pandas as pd
import random
import os


doc = """
Your app description
"""

#-----------------------------------------------------------------------------
# MODELS
class C(BaseConstants):
    NAME_IN_URL = 'SBC_S1_t1_'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 15 #setting the full length to ensure that data contains all necesasry info.

    ENDOWMENT = cu(15)
    # TREATMENT ORDER:
    # 0 = static, buy at t=1
    # 1 = static, buy at t=2
    # 2 = dynamic, option
    # 3 = dynamic, refund
    PRICES_T1  = [[ 0 for i in range(15) ] for j in range(4)]
    # outside is for treatment: 0 to 3
    PRICES_T1[0] = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 8, 9, 11, 12]
    PRICES_T1[2] = [8, 0, 0, 10, 1, 2, 1, 2, 3, 2, 3, 4, 7, 8, 9]
    PRICES_T1[3] = [8, 12, 10, 10, 11, 12, 9, 10, 11, 8, 9, 10, 8, 9, 10]

    PRICES_T2 = [[0 for i in range(15) ] for j in range(4)]
    PRICES_T1[1] = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 8, 9, 11, 12]
    PRICES_T2[2] = [0, 12, 10, 0, 10, 10, 8, 8, 8, 6, 6, 6, 1, 1, 1]
    PRICES_T2[3] = [0, 12, 10, 0, 10, 10, 8, 8, 8, 6, 6, 6, 1, 1, 1]

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    x = models.CurrencyField()
    # initial purchase variable. 
    purchase = models.BooleanField(choices=[[True, 'Yes'], [False, 'No']], widget=widgets.RadioSelectHorizontal, label='')#, label='Do you want to purchase this lottery ticket?', )
    
    # we start by introducing the revised purchase to every period. 
    revised_purchase = models.BooleanField(choices=[[True, 'Yes'], [False, 'No']], widget=widgets.RadioSelectHorizontal, label='')#, label='Do you want to purchase this lottery ticket?', )


    price_t1 = models.IntegerField()
    price_t2 = models.IntegerField()

    selected_round = models.IntegerField()
    random_draw_1 = models.IntegerField()
    random_draw_2 = models.IntegerField()
    treatment = models.StringField()
#-----------------------------------------------------------------------------




#-----------------------------------------------------------------------------
# FUNCTIONS:
def draw_order(player: Player):
    session = player.session
    subsession = player.subsession
    participant = player.participant
    if (subsession.round_number == 1) or (participant.treatment == 1):
        import random
        indexes = list( range(len(C.PRICES_T1[participant.treatment])) )
        random.shuffle(indexes)

        pricelist_t1 = list( [C.PRICES_T1[participant.treatment][j] for j in indexes ] )
        pricelist_t2 = list( [C.PRICES_T2[participant.treatment][j] for j in indexes ] )
        participant.price_order_t1 = pricelist_t1
        participant.price_order_t2 = pricelist_t2
        participant.indexes = indexes

        random_draw_1 = random.randint(0, 1)
        participant.random_draw_1 = random_draw_1

        random_draw_2 = random.randint(0, 1)
        participant.random_draw_2 = random_draw_2




def save_to_csv(data_dict, filename="output.csv"):
    # Convert dict to DataFrame (1 row)
    df_new = pd.DataFrame([data_dict])

    # If file exists, append without header
    if os.path.exists(filename):
        df_new.to_csv(filename, mode="a", index=False, header=False)
    else:
        df_new.to_csv(filename, mode="w", index=False, header=True)



#-----------------------------------------------------------------------------
# PAGES
class ExperimentStarts(Page):
    form_model = 'player'
    @staticmethod
    def is_displayed(player: Player):
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
            two_heads_sum = 2*session.config['A_BAR'],
            heads_tails_sum = session.config['A_BAR'] + participant.x_draw + 2,
            example_sum= session.config['A_BAR'] + participant.x_draw
        )


class Decision(Page):
    form_model = 'player'
    form_fields = ['purchase']
    @staticmethod
    def is_displayed(player: Player):
        session = player.session
        subsession = player.subsession
        participant = player.participant
        player.price_t1 = (participant.price_order_t1[subsession.round_number-1] )
        player.price_t2 = ( participant.price_order_t2[subsession.round_number-1] )
        player.x =  ( participant.x_draw )
        if player.participant.treatment == 1:
            # for the S2 treatment block the purchase as true.
            player.purchase = True
            player.revised_purchase = player.purchase
            return False
        else:
            return True

    @staticmethod
    def before_next_page(player, timeout_happened):

        # generate the random draws in the first stage of the experiment:
        player.random_draw_1 = int(player.participant.random_draw_1)
        player.random_draw_2 = int(player.participant.random_draw_2)

        player.revised_purchase = player.purchase

        index = player.participant.indexes[player.subsession.round_number-1]
#        save_to_csv({
#            "participant.label": player.participant.label,
#            "participant.x_draw": player.participant.x_draw,
#            "participant.treatment": player.participant.treatment,
#            "player.price_t1": (player.price_t1),
#			"player.price_t2": (player.price_t2),
#            "participant.indexes": index,
#			"player.random_draw_1": player.random_draw_1,
#			"player.random_draw_2": player.random_draw_2,
#            "player.purchase": player.purchase,
#            "player.revised_purchase": player.revised_purchase,
#                # add other variables
#        })

    @staticmethod
    def vars_for_template(player: Player):
        session = player.session
        participant = player.participant
        return dict(
            two_heads_sum = 2*session.config['A_BAR'],
            heads_tails_sum = session.config['A_BAR'] + participant.x_draw + 2,
            example_sum= session.config['A_BAR'] + participant.x_draw
        )

# what should we record for the second stage? 
class Results(Page):
    timeout_seconds = 10  # Timeout after 10 seconds
    
    def is_displayed(player: Player):
        subsession = player.subsession
        return (subsession.round_number == C.NUM_ROUNDS) 

    @staticmethod
    def before_next_page(player, timeout_happened):
        if player.participant.treatment == 1:
            for r in range(1, C.NUM_ROUNDS + 1):
                p = player.in_round(r)
                save_to_csv({
                    "participant.label": player.participant.label,
                    "participant.x_draw": player.participant.x_draw,
                    "participant.treatment": player.participant.treatment,
                    "player.price_t1": (p.price_t1),
			        "player.price_t2": (p.price_t2),
                    "participant.indexes": player.participant.indexes[r - 1],
			        "player.random_draw_1": player.participant.random_draw_1,
			        "player.random_draw_2": player.participant.random_draw_2,
                    "player.purchase":         p.purchase,
                    "player.revised_purchase": p.revised_purchase,
                })

#-----------------------------------------------------------------------------


# REVISION PAGE
class RevisionPage(Page):
    form_model = 'player'

    @staticmethod
    def is_displayed(player: Player):
        return (player.round_number == C.NUM_ROUNDS) and (player.participant.treatment != 1)

    @staticmethod
    def live_method(player: Player, data: dict):
        round_num = data['round']          # which round's decision is being revised
        revised = data['revised_purchase'] # the new True/False value
        player.in_round(round_num).revised_purchase = revised  # writes to that round's player object

    @staticmethod
    def vars_for_template(player: Player):
        past = []
        for r in range(1, C.NUM_ROUNDS + 1):
            p = player.in_round(r)
            past.append(dict(
                round=r,
                price_t1=p.price_t1,
                price_t2=p.price_t2,
                purchase=p.purchase,
                revised_purchase=p.revised_purchase,
            ))
        return dict(past_decisions=past)
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        for r in range(1, C.NUM_ROUNDS + 1):
            p = player.in_round(r)
            save_to_csv({
            "participant.label": player.participant.label,
            "participant.x_draw": player.participant.x_draw,
            "participant.treatment": player.participant.treatment,
            "player.price_t1": (p.price_t1),
			"player.price_t2": (p.price_t2),
            "participant.indexes": player.participant.indexes[r - 1],
			"player.random_draw_1": player.participant.random_draw_1,
			"player.random_draw_2": player.participant.random_draw_2,
            "player.purchase":         p.purchase,
            "player.revised_purchase": p.revised_purchase,
            })





#-----------------------------------------------------------------------------
# Final completion page
class CompletionPage(Page):
    timeout_seconds = 60  # 1 minute to read the message

    @staticmethod
    def is_displayed(player: Player):
        subsession = player.subsession
        return subsession.round_number == C.NUM_ROUNDS


# ORDER
page_sequence = [ExperimentStarts,
                Decision, 
                RevisionPage,
                Results,
                CompletionPage]
#-----------------------------------------------------------------------------