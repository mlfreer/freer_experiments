from otree.api import *
import random
import math


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'attention_welfare_choice'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 30

    # within and between budget choices:
    NUMBER_OF_DOUBLETONES = 10
    NUMBER_OF_TRIPLETONES = 20
    NUMBER_OF_BETWEEN_MENU_CHOICES = 20

    # DEFINING THE UNIVERSAL SET
    UNIVERSAL_X = [0, 1, 2, 3, 4] # OUTCOMES IN THE STATE OF THE WORLD X
    UNIVERSAL_Y = [4, 3, 2, 1, 0] # OUTCOMES IN THE STATE OF THE WORLD Y

    # DEFINING THE DECOYS:
    DECOY_X = [-1, -2, -3, -4, -5]
    DECOY_Y = [-1, -2, -3, -4, -5]
    # decoys correspond to the corresponding index of the alternative

    # DOUBLETONES
    # formed as the all pairs using the indexes in the array of the universal alternatives
    DOUBLETONES = [[0,1], [0,2], [0,3], [0,4], [1,2], [1,3], [1,4], [2,3], [2,4], [3,4]]

    # TRIPLETONES
    # defined by the decoy to be used in the tripletone
    # each tripletone takes the corresponding (by modulo) doubletone and adds a decoy
    TRIPLETONES = [0, 0, 0, 0, 1, 1, 1, 2, 2, 3, 1, 2, 3, 4, 2, 3, 4, 3, 4, 4]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


#----------------------------------------------------------
# PLAYER CLASS
#----------------------------------------------------------
class Player(BasePlayer):
    # decision variables:
    doubletone_choice = models.IntegerField()
    tripletone_choice = models.IntegerField()
    between_budget_choice = models.IntegerField()

    # budget types:
    is_doubletone = models.BooleanField(initial = False)
    is_tripletone = models.BooleanField(initial = False)
    is_between_menu_choice = models.BooleanField(initial = False)

    # doubletone order
    doubletone_index = models.IntegerField()
    # tripletone order
    tripletone_index = models.IntegerField()


#----------------------------------------------------------
# FUNCTIONS
#----------------------------------------------------------
def creating_session(subsession):
    for p in subsession.get_players():
        set_doubletones_order(p)
        set_tripletones_order(p)

def set_doubletones_order(player: Player):
    indices = [0,1,2,3,4,5,6,7,8,9]
    random.shuffle(indices)
    players = player.in_all_rounds()

    i=0
    for p in players:
        if (i<=9):
            p.doubletone_index = indices[i]
            p.is_doubletone = True
        i+=1

def set_tripletones_order(player: Player):
    indices = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]
    random.shuffle(indices)
    players = player.in_all_rounds()

    i=0
    for p in players:
        if (i>=10) and (i<=29):
            p.tripletone_index = indices[i-10]
            p.is_tripletone = True
        i+=1


#----------------------------------------------------------
# PAGES
#----------------------------------------------------------
class Doubletone_Decision(Page):
    def is_displayed(player):
        return player.subsession.round_number <= C.NUMBER_OF_DOUBLETONES
    form_model = 'player'
    form_fields = ['doubletone_choice']

    @staticmethod
    def vars_for_template(player):
        temp = C.DOUBLETONES[player.doubletone_index]
#       print(temp[0])
        return dict(
            option1_x = C.UNIVERSAL_X[temp[0]],
            option1_y = C.UNIVERSAL_Y[temp[0]],
            option2_x = C.UNIVERSAL_X[temp[1]],
            option2_y = C.UNIVERSAL_Y[temp[1]]
            )
    #------------------------------------------------------------

class Tripletone_Decision(Page):
    def is_displayed(player):
        return (player.subsession.round_number > C.NUMBER_OF_DOUBLETONES) and (player.subsession.round_number <= C.NUMBER_OF_DOUBLETONES + C.NUMBER_OF_TRIPLETONES)
    form_model = 'player'
    form_fields = ['tripletone_choice']

    @staticmethod
    def vars_for_template(player):
        decoy_index = C.TRIPLETONES[player.tripletone_index]
        option_index = C.DOUBLETONES[(player.tripletone_index+1) % C.NUMBER_OF_DOUBLETONES - 1]
        return dict(
            option1_x = C.UNIVERSAL_X[option_index[0]],
            option1_y = C.UNIVERSAL_Y[option_index[0]],
            option2_x = C.UNIVERSAL_X[option_index[1]],
            option2_y = C.UNIVERSAL_Y[option_index[1]],
            decoy_x = C.DECOY_X[decoy_index],
            decoy_y = C.DECOY_Y[decoy_index]
            )


page_sequence = [
            Doubletone_Decision,
            Tripletone_Decision
            ]
