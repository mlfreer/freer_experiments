from otree.api import *
import random
import math


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'attention_welfare_choice'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 50

    SHOW_UP_FEE = cu(4)
    # within and between budget choices:
    NUMBER_OF_DOUBLETONES = 10
    NUMBER_OF_TRIPLETONES = 20
    NUMBER_OF_BETWEEN_MENU_CHOICES = 20

    # QUIZ ANSWERS:
    QUIZ1_WITHIN = 2
    QUIZ2_WITHIN = 1
    QUIZ1_BETWEEN = 1
    QUIZ2_BETWEEN = 1

    # DEFINING THE UNIVERSAL SET
    UNIVERSAL_X = [15, 11, 9, 6, 3] # OUTCOMES IN THE STATE OF THE WORLD X
    UNIVERSAL_Y = [1, 5, 7, 10, 13] # OUTCOMES IN THE STATE OF THE WORLD Y

    # DEFINING THE DECOYS:
    DECOY_X = [14, 10, 8, 5, 2]
    DECOY_Y = [0, 4, 6, 9, 12]
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
    # order of representation
    alt_order = models.IntegerField()

    # decision variables:
    doubletone_choice = models.IntegerField()
    tripletone_choice = models.IntegerField()
    between_menu_choice = models.IntegerField()

    # budget types:
    is_doubletone = models.BooleanField(initial = False)
    is_tripletone = models.BooleanField(initial = False)
    is_between_menu_choice = models.BooleanField(initial = False)

    # doubletone order
    doubletone_index = models.IntegerField(initial=-1)
    # tripletone order
    tripletone_index = models.IntegerField(initial=-1)
    # between menu order
    between_menu_index = models.IntegerField(initial=-1)

    payment_round_within = models.IntegerField(initial=-1,min=1,max=30)
    payment_round_between = models.IntegerField(initial=-1,min=31,max=50)

    payment_within = models.IntegerField()
    payment_between = models.IntegerField()

    # additinal variables to keep track of:
    doubletone_choice_x = models.IntegerField()
    doubletone_choice_y = models.IntegerField()
    tripletone_choice_x = models.IntegerField()
    tripletone_choice_y = models.IntegerField()

    # quiz questions
    within_q1 = models.IntegerField()
    within_q2 = models.IntegerField()
    between_q1 = models.IntegerField()
    between_q2 = models.IntegerField()


#----------------------------------------------------------
# FUNCTIONS
#----------------------------------------------------------

#----------------------------------------------------------
# CREATING SESSION:
#----------------------------------------------------------
def creating_session(subsession):
    for p in subsession.get_players():
        set_doubletones_and_tripletones(p)
        set_between_menus_order(p)
    #----------------------------------------------------------

def set_doubletones_and_tripletones(player: Player):
    players = player.in_all_rounds()
    doubletones = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1]
    random.shuffle(doubletones)
    
    i=0
    for p in players:
        p.is_doubletone = False
        p.is_tripletone = False
        if (i<=29):
            if (doubletones[i] == 1):
                p.is_doubletone = True
            else:
                p.is_tripletone = True
        i+=1
    set_doubletones_order(player)
    set_tripletones_order(player)
    #----------------------------------------------------------


def set_doubletones_order(player: Player):
    indices = [0,1,2,3,4,5,6,7,8,9]
    random.shuffle(indices)
    players = player.in_all_rounds()

    i=0
    for p in players:
#        print(p.is_doubletone)
        if (p.is_doubletone==True):
            p.doubletone_index = indices[i]
            i+=1
    #----------------------------------------------------------

        

def set_tripletones_order(player: Player):
    indices = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]
    random.shuffle(indices)
    players = player.in_all_rounds()

    i=0
    for p in players:
        if (p.is_tripletone==True):
            p.tripletone_index = indices[i]
            i+=1
    #----------------------------------------------------------


def set_between_menus_order(player: Player):
    indices = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]
    random.shuffle(indices)
    players = player.in_all_rounds()

    i=0
    for p in players:
        if (i>=30):
            p.between_menu_index = indices[i-30]
            p.is_between_menu_choice = True
        i+=1
    #----------------------------------------------------------

#----------------------------------------------------------
# COMPUTING PAYOFF
#----------------------------------------------------------
def set_payoff(player: Player):
    # remove magic numbers later:
    player.payment_round_within = random.randint(1,30)
    player.payment_round_between = random.randint(31,50)

    p_within = player.in_round(player.payment_round_within)
    p_between = player.in_round(player.payment_round_between)

    within_payment = get_within_payment(p_within)
    between_payment = get_between_payment(p_between)

    player.payment_within = within_payment
    player.payment_between = between_payment
    player.payoff = cu(player.payment_within) + cu(player.payment_between) + C.SHOW_UP_FEE

def get_between_payment(player: Player):
#    p_between = player.in_round(player.payment_round_between)
    p_between = player

    coin_within = random.randint(0,1)
    coin_between = random.randint(0,1)

    if p_between.between_menu_choice == 0:
        if coin_within == 0:
            between_payment = p_between.doubletone_choice_x
        else:
            between_payment = p_between.doubletone_choice_y
    elif p_between.between_menu_choice == 1:
        if coin_within == 0:
            between_payment = p_between.tripletone_choice_x
        else:
            between_payment = p_between.tripletone_choice_y
    return between_payment


def get_within_payment(player: Player):
    # flipping the coins:
    # 0 = heads
    # 1 = tails
    coin_within = random.randint(0,1)
    coin_between = random.randint(0,1)

    p_within = player
    # recover the choices
    if p_within.is_doubletone == True:
        temp = C.DOUBLETONES[p_within.doubletone_index]
        choice_within = temp[p_within.doubletone_choice]
        if coin_within == 0:
            within_payment = C.UNIVERSAL_X[choice_within]
        else:
            within_payment = C.UNIVERSAL_Y[choice_within]
    elif p_within.is_tripletone == True:
        if p_within.tripletone_choice == 2:
            choice_within = C.TRIPLETONES[p_within.tripletone_index]
            if coin_within == 0:
                within_payment = C.DECOY_X[choice_within]
            else:
                within_payment = C.DECOY_Y[choice_within]
        else:
            if (player.tripletone_index+1) % C.NUMBER_OF_DOUBLETONES >0:
                option = C.DOUBLETONES[(player.tripletone_index+1) % C.NUMBER_OF_DOUBLETONES - 1]
            else:
                option = C.DOUBLETONES[0]

            within_choice = p_within.tripletone_choice

            if coin_within == 0:
                within_payment = C.UNIVERSAL_X[option[within_choice]]
            else:
                within_payment = C.UNIVERSAL_Y[option[within_choice]]

    return within_payment



    
    # determine the payment
    # push them to the payoff variable so collides nicely with payment table


#----------------------------------------------------------
# DECISION PAGES
#----------------------------------------------------------
class Doubletone_Decision(Page):
    def is_displayed(player):
        return player.is_doubletone == True
    form_model = 'player'
    form_fields = ['doubletone_choice']

    @staticmethod
    def vars_for_template(player):
        temp = C.DOUBLETONES[player.doubletone_index]
        player.alt_order = random.randint(0,1)
#       print(temp[0])
        return dict(
            option1_x = C.UNIVERSAL_X[temp[0]],
            option1_y = C.UNIVERSAL_Y[temp[0]],
            option2_x = C.UNIVERSAL_X[temp[1]],
            option2_y = C.UNIVERSAL_Y[temp[1]],
            total_problems = C.NUMBER_OF_DOUBLETONES + C.NUMBER_OF_TRIPLETONES,
            order = player.alt_order
            )
    #------------------------------------------------------------

class Tripletone_Decision(Page):
    def is_displayed(player):
        return player.is_tripletone == True
    form_model = 'player'
    form_fields = ['tripletone_choice']

    @staticmethod
    def vars_for_template(player):
        decoy_index = C.TRIPLETONES[player.tripletone_index]
        if (player.tripletone_index+1) % C.NUMBER_OF_DOUBLETONES >0:
            option_index = C.DOUBLETONES[(player.tripletone_index+1) % C.NUMBER_OF_DOUBLETONES - 1]
        else:
            option_index = C.DOUBLETONES[0]

        player.alt_order = random.randint(0,5)
        return dict(
            option1_x = C.UNIVERSAL_X[option_index[0]],
            option1_y = C.UNIVERSAL_Y[option_index[0]],
            option2_x = C.UNIVERSAL_X[option_index[1]],
            option2_y = C.UNIVERSAL_Y[option_index[1]],
            decoy_x = C.DECOY_X[decoy_index],
            decoy_y = C.DECOY_Y[decoy_index],
            total_problems = C.NUMBER_OF_DOUBLETONES + C.NUMBER_OF_TRIPLETONES,
            order = player.alt_order
            )
    #------------------------------------------------------------

class Between_Menu_Decision(Page):
    def is_displayed(player):
        return (player.subsession.round_number> C.NUMBER_OF_DOUBLETONES + C.NUMBER_OF_TRIPLETONES)
    form_model = 'player'
    form_fields = ['between_menu_choice']

    @staticmethod
    def before_next_page(player, timeout_happened):
        if player.round_number == C.NUM_ROUNDS:
            set_payoff(player)



    @staticmethod
    def vars_for_template(player):
        decoy_index = C.TRIPLETONES[player.between_menu_index]
        option_index = C.DOUBLETONES[(player.between_menu_index+1) % C.NUMBER_OF_DOUBLETONES - 1]

        if (player.between_menu_index+1) % C.NUMBER_OF_DOUBLETONES > 0:
            doubletone_index = (player.between_menu_index+1) % C.NUMBER_OF_DOUBLETONES-1
        else:
            doubletone_index = 0

        # recovering choice:
        players = player.in_all_rounds()
        for p in players:
            if (p.is_doubletone==True) and (p.doubletone_index == doubletone_index):
                doubletone_choice = p.doubletone_choice
            if (p.is_tripletone==True) and (p.tripletone_index == decoy_index):
                tripletone_choice = p.tripletone_choice

        if tripletone_choice < 2:
            tripletone_choice_x = C.UNIVERSAL_X[option_index[tripletone_choice]]
            tripletone_choice_y = C.UNIVERSAL_Y[option_index[tripletone_choice]]
        else:
            tripletone_choice_x = C.DECOY_X[decoy_index]
            tripletone_choice_y = C.DECOY_Y[decoy_index]

        player.doubletone_choice_x = C.UNIVERSAL_X[option_index[doubletone_choice]]
        player.doubletone_choice_y = C.UNIVERSAL_Y[option_index[doubletone_choice]]
        player.tripletone_choice_x = tripletone_choice_x
        player.tripletone_choice_y = tripletone_choice_y

        player.alt_order = random.randint(0,1)

        return dict(
            option1_x = C.UNIVERSAL_X[option_index[0]],
            option1_y = C.UNIVERSAL_Y[option_index[0]],
            option2_x = C.UNIVERSAL_X[option_index[1]],
            option2_y = C.UNIVERSAL_Y[option_index[1]],
            decoy_x = C.DECOY_X[decoy_index],
            decoy_y = C.DECOY_Y[decoy_index],
            doubletone_choice_x = C.UNIVERSAL_X[option_index[doubletone_choice]],
            doubletone_choice_y = C.UNIVERSAL_Y[option_index[doubletone_choice]],
            tripletone_choice_x = tripletone_choice_x,
            tripletone_choice_y = tripletone_choice_y,
            total_problems = C.NUMBER_OF_BETWEEN_MENU_CHOICES,
            problem_number = player.subsession.round_number - C.NUMBER_OF_DOUBLETONES - C.NUMBER_OF_TRIPLETONES,
            order = player.alt_order
            )
        #------------------------------------------------------------

#----------------------------------------------------------
# RESULTS:
#----------------------------------------------------------
class Results(Page):
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player):
        return dict(
            within_round = player.payment_round_within,
            between_round = player.payment_round_between - C.NUMBER_OF_DOUBLETONES - C.NUMBER_OF_TRIPLETONES,
            within_payment = cu(player.payment_within),
            between_payment = cu(player.payment_between),
            showup = C.SHOW_UP_FEE
            )

#----------------------------------------------------------
# INSTRUCTIONS
#----------------------------------------------------------
class Instructions_Overview(Page):
    def is_displayed(player):
        return (player.subsession.round_number == 1)

class Instructions_Within_Menu(Page):
    def is_displayed(player):
        return (player.subsession.round_number == 1)

class Instructions_Between_Menu(Page):
    def is_displayed(player):
        return (player.subsession.round_number == C.NUMBER_OF_DOUBLETONES+C.NUMBER_OF_TRIPLETONES)
    #----------------------------------------------------------

#----------------------------------------------------------
# QUIZ PAGES
#----------------------------------------------------------
class Quiz1_within(Page):
    # outcomes are equally likely
    def is_displayed(player):
        return (player.subsession.round_number == 1)

    form_model = 'player'
    form_fields = ['within_q1']

    def error_message(player, value):
        if value['within_q1'] != C.QUIZ1_WITHIN:
            result = 'Wrong Answer. Please Try Again.'
            return result
    #----------------------------------------------------------



class Quiz2_within(Page):
    # realization and payment
    def is_displayed(player):
        return (player.subsession.round_number == 1)

    form_model = 'player'
    form_fields = ['within_q2']

    def error_message(player, value):
        if value['within_q2'] != C.QUIZ2_WITHIN:
            result = 'Wrong Answer. Please Try Again.'
            return result
    #----------------------------------------------------------

class Quiz1_between(Page):
    # realization and payment
    def is_displayed(player):
        return (player.subsession.round_number == C.NUMBER_OF_DOUBLETONES+C.NUMBER_OF_TRIPLETONES)

    form_model = 'player'
    form_fields = ['between_q1']

    def error_message(player, value):
        if value['between_q1'] != C.QUIZ1_BETWEEN:
            result = 'Wrong Answer. Please Try Again.'
            return result
    #----------------------------------------------------------


class Quiz2_between(Page):
    # realization and payment
    def is_displayed(player):
        return (player.subsession.round_number == C.NUMBER_OF_DOUBLETONES+C.NUMBER_OF_TRIPLETONES)

    form_model = 'player'
    form_fields = ['between_q2']

    def error_message(player, value):
        if value['between_q2'] != C.QUIZ2_BETWEEN:
            result = 'Wrong Answer. Please Try Again.'
            return result
    #----------------------------------------------------------



#------------------------------------------------------------
# PAGE SEQUENCE
#------------------------------------------------------------
page_sequence = [
            Instructions_Overview,
            Instructions_Within_Menu,
            Quiz1_within,
            Quiz2_within,
            Doubletone_Decision,
            Tripletone_Decision,
            Instructions_Between_Menu,
            Quiz1_between,
            Quiz2_between,
            Between_Menu_Decision,
            Results
            ]
