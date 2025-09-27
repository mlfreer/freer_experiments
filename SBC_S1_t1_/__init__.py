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
    PRICES_T1 = (cu(5), cu(6), cu(7), cu(8), cu(9), cu(10), cu(11), cu(12), cu(13), cu(14), cu(15))

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
    price = models.CurrencyField()
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
        pricelist = list(C.PRICES_T1)
        random.shuffle(pricelist)
        participant.price_order = pricelist


def calculate_payoff(player: Player):
    session = player.session
    participant = player.participant
    print("x")
    print(player.x)
    
    import random
    random_round = random.randint(1, C.NUM_ROUNDS)
    player.selected_round = random_round
    participant.selected_round = random_round
    print("selected round was")
    print(player.selected_round)
    player_decision = player.in_round(random_round).purchase
    print("decision was")
    print(player_decision)
    
    random_draw_1 = random.randint(0, 1)
    player.random_draw_1 = random_draw_1
    print("first flip")
    print(player.random_draw_1)    
    random_draw_2 = random.randint(0, 1)
    player.random_draw_2 = random_draw_2
    print("second flip")
    print(player.random_draw_2)
    
    if player_decision is False:
        player.payoff = C.ENDOWMENT
    
    if player_decision is True:
        totalpayoff = C.ENDOWMENT - player.in_round(random_round).price
        print("until first part payoff")
        print(totalpayoff)    
        if random_draw_1 == 1:
            totalpayoff = totalpayoff + player.x
        elif random_draw_1 == 0:
            totalpayoff = totalpayoff + session.config['A_BAR']
        player.payoff = totalpayoff
    
    print(player.payoff)

#-----------------------------------------------------------------------------
# PAGES
class Instructions(Page):
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
        player.price = participant.price_order[subsession.round_number-1]
        player.x = participant.x_draw
        return True


# what should we record for the second stage? 
class Results(Page):
    def before_next_page(player, timeout_happened):
        if player.participant.label and player.participant.label.strip():
            save_to_csv({
                "prolificID": player.participant.label,
                # add other variables
            })
#-----------------------------------------------------------------------------



#-----------------------------------------------------------------------------
# ORDER
page_sequence = [Instructions, 
                Decision, 
                Results]
#-----------------------------------------------------------------------------