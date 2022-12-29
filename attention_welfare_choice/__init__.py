from otree.api import *
import random
import math


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'attention_welfare_choice'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 10

    # within and between budget choices:
    WITHIN_BUDGET_CHOICE = 0
    BETWEEN_BUDGET_CHOICE = 1

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
    within_budget_choice = models.IntegerField()
    between_budget_choice = models.IntegerField()

    # budget type (0 -- within, 1 -- between):
    budget_type = models.IntegerField()
    is_doubletone = models.BooleanField(initial = True)

    # doubletone order
    doubletone_index = models.IntegerField()


#----------------------------------------------------------
# FUNCTIONS
#----------------------------------------------------------
def creating_session(subsession):
    for p in subsession.get_players():
        set_doubletones_order(p)

def set_doubletones_order(player: Player):
    indices = [0,1,2,3,4,5,6,7,8,9]
    random.shuffle(indices)
    players = player.in_all_rounds()

    i=0
    for p in players:
        p.doubletone_index = indices[i]
        i+=1




#----------------------------------------------------------
# PAGES
#----------------------------------------------------------
class Within_Budget_Decision(Page):
#    def is_displayed(player):
#        return player.budget_type == C.WITHIN_BUDGET_CHOICE
    form_model = 'player'
    form_fields = ['within_budget_choice']

    @staticmethod
    def vars_for_template(player):
        temp = C.DOUBLETONES[player.doubletone_index]
        print(temp[0])
        return dict(
            option1_x = C.UNIVERSAL_X[temp[0]],
            option1_y = C.UNIVERSAL_Y[temp[0]],
            option2_x = C.UNIVERSAL_X[temp[1]],
            option2_y = C.UNIVERSAL_Y[temp[1]]
            )
    #------------------------------------------------------------



page_sequence = [
            Within_Budget_Decision
            ]
