from otree.api import *
import pandas as pd
import os


doc = """
Your app description
"""

#-----------------------------------------------------------------------------
# MODELS
class C(BaseConstants):
    NAME_IN_URL = 'SBC_S1_t1_'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    ENDOWMENT = cu(15)
    # TREATMENT ORDER:
    # 0 = static, buy at t=1
    # 1 = static, buy at t=2
    # 2 = dynamic, option
    # 3 = dynamic, refund
    PRICES_T1  = [[cu(0) for i in range(15) ] for j in range(4)]
    # outside is for treatment: 0 to 3
    PRICES_T1[0] = [cu(5), cu(6), cu(7), cu(8), cu(9), cu(10), cu(11), cu(12), cu(13), cu(14), cu(15)]
    PRICES_T1[2] = [cu(0), cu(12), cu(10), cu(0), cu(10), cu(10), cu(8), cu(8), cu(8), cu(6), cu(6), cu(6), cu(1), cu(1), cu(1)]

    PRICES_T2 = [[0 for i in range(15) ] for j in range(4)]
    PRICES_T2[2] = (cu(8), cu(0), cu(0), cu(10), cu(1), cu(2), cu(1), cu(2), cu(3), cu(2), cu(3), cu(4), cu(7), cu(8), cu(9))

def save_to_csv(data_dict, filename="output.csv"):
    # Convert dict to DataFrame (1 row)
    df_new = pd.DataFrame([data_dict])

    # If file exists, append without header
    if os.path.exists(filename):
        df_new.to_csv(filename, mode="a", index=False, header=False)
    else:
        df_new.to_csv(filename, mode="w", index=False, header=True)

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    x = models.CurrencyField()
    purchase = models.BooleanField(choices=[[True, 'Yes'], [False, 'No']], widget=widgets.RadioSelectHorizontal, label='')#, label='Do you want to purchase this lottery ticket?', )
    
    price_t1 = models.CurrencyField()
    price_t2 = models.CurrencyField()

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
    if subsession.round_number == 1:
        import random
        indexes = list( range(len(C.PRICES_T1[participant.treatment])) )
        random.shuffle(indexes)

        pricelist_t1 = list( [C.PRICES_T1[participant.treatment][j] for j in indexes ] )
        pricelist_t2 = list( [C.PRICES_T2[participant.treatment][j] for j in indexes ] )
        participant.price_order_t1 = pricelist_t1
        participant.price_order_t2 = pricelist_t2


def calculate_payoff(player: Player):
    session = player.session
    participant = player.participant
    print("x")
    print(player.x)
    
    import random
    random_round = random.randint(1, C.NUM_ROUNDS)
    player.selected_round = random_round
    participant.selected_round = random_round
#    print("selected round was")
#    print(player.selected_round)
    player_decision = player.in_round(random_round).purchase
#    print("decision was")
#    print(player_decision)
    
    random_draw_1 = random.randint(0, 1)
    player.random_draw_1 = random_draw_1
#    print("first flip")
#    print(player.random_draw_1)    
    random_draw_2 = random.randint(0, 1)
    player.random_draw_2 = random_draw_2
#    print("second flip")
#    print(player.random_draw_2)
    
    if player_decision is False:
        player.payoff = C.ENDOWMENT
    
    if player_decision is True:
        totalpayoff = C.ENDOWMENT - player.in_round(random_round).price_t1 - player.in_round(random_round).price_t2
 #       print("until first part payoff")
 #       print(totalpayoff)    
        if random_draw_1 == 1:
            totalpayoff = totalpayoff + player.x
        elif random_draw_1 == 0:
            totalpayoff = totalpayoff + session.config['A_BAR']
        player.payoff = totalpayoff
    
#    print(player.payoff)

#-----------------------------------------------------------------------------
# PAGES
class Welcome(Page):
    form_model = 'player'
    @staticmethod
    def is_displayed(player: Player):
        session = player.session
        subsession = player.subsession
        participant = player.participant
        if subsession.round_number == 1:
            player.x = participant.x_draw
            draw_order(player)
            return True


class Decision(Page):
    form_model = 'player'
    form_fields = ['purchase']
    @staticmethod
    def is_displayed(player: Player):
        session = player.session
        subsession = player.subsession
        participant = player.participant
        player.price_t1 = participant.price_order_t1[subsession.round_number-1]
        player.price_t2 = participant.price_order_t2[subsession.round_number-1]
        player.x = participant.x_draw
        return True


# what should we record for the second stage? 
class Results(Page):
    def is_displayed(player: Player):
        subsession = player.subsession
        return subsession.round_number == C.NUM_ROUNDS


    @staticmethod
    def before_next_page(player, timeout_happened):
        if player.participant.label and player.participant.label.strip():
            save_to_csv({
                "prolificID": player.participant.label,
                # add other variables
            })
#-----------------------------------------------------------------------------



#-----------------------------------------------------------------------------
# ORDER
page_sequence = [Welcome,
                Decision, 
                Results]
#-----------------------------------------------------------------------------