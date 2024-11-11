from otree.api import *
import random
import math


doc = """
Application for simple arbitration experiment.
Dominant strategy mechanism.
"""

#-----------------------------------------------------------------------------------
# MODELS
#-----------------------------------------------------------------------------------
class C(BaseConstants):
    NAME_IN_URL = 'Simple_NF_SS'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 20
    # replace with 20 for the real thing

    preferences = [0 for i in range(0,6)]
    # defining the vector of preferences:
    preferences[0] = [12, 8, 2] # abc
    preferences[1] = [12, 2, 8] # acb
    preferences[2] = [8, 12, 2] # bac
    preferences[3] = [2, 12, 8] # bca
    preferences[4] = [8, 2, 12] # cab
    preferences[5] = [2, 8, 12] # cba

    alternatives = ['blue', 'green', 'orange'] #, 'purple']

    LABELS = ['A','B','C', 'D', 'E']

    outcomes = [0 for i in range(0,5)]
    outcomes[0] = [0, 0, 0, 0, 0]
    outcomes[1] = [0, 1, 1, 0, 1]
    outcomes[2] = [0, 1, 1, 2, 1]
    outcomes[3] = [0, 0, 2, 2, 2]
    outcomes[4] = [0, 1, 1, 2, 2]


class Subsession(BaseSubsession):
    paying_round = models.IntegerField(min=1,max=C.NUM_ROUNDS,initial=0)


class Group(BaseGroup):
    # variable to determine the group level preference ordering
    blue = models.IntegerField(min=0,max=2)
    green = models.IntegerField(min=0,max=2)
    orange = models.IntegerField(min=0,max=2)

    # defining the ranking list:
    rank1 = models.IntegerField(min=0,max=2)
    rank2 = models.IntegerField(min=0,max=2)
    rank3 = models.IntegerField(min=0,max=2)

    # reordering of the choices:
    s1 = models.IntegerField(min=0,max=4)
    s2 = models.IntegerField(min=0,max=4)
    s3 = models.IntegerField(min=0,max=4)
    s4 = models.IntegerField(min=0,max=4)
    s5 = models.IntegerField(min=0,max=4)

    # reordering of the others choices:
    c1 = models.IntegerField(min=0,max=4)
    c2 = models.IntegerField(min=0,max=4)
    c3 = models.IntegerField(min=0,max=4)
    c4 = models.IntegerField(min=0,max=4)
    c5 = models.IntegerField(min=0,max=4)

    # final choice
    Collective_Choice = models.IntegerField(min=0,max=3,initial=-1)
    


class Player(BasePlayer):
    # variable to store the type:
    MyPreferences = models.IntegerField(min=-1, max=3, initial=-1)

    # variable to store the voting:
    vote  = models.IntegerField(min=0,max=4)
    earnings = models.IntegerField(min=0,max=20)


#-----------------------------------------------------------------------------------
# FUNCTIONS
#-----------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------
# session level
def creating_session(session: Subsession):
    session.group_randomly(fixed_id_in_group=False)

def set_paying_round(session: Subsession):
    p_round = random.randint(1,C.NUM_ROUNDS)
    s = session.in_round(C.NUM_ROUNDS)
    s.paying_round = p_round
#-----------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------
# group level
def set_ordering(group: Group):
    numeric = [0, 1, 2]
    random.shuffle(numeric)
    # Setting up a random order:
    group.blue = numeric[0]
    group.green = numeric[1]
    group.orange = numeric[2]

#   print(numeric[0])

    options = [0,1,2]
    random.shuffle(options)

    # Recording the ranking
    group.rank1 = options[0]
    group.rank2 = options[1]
    group.rank3 = options[2]

    numeric = [0, 1, 2, 3, 4]
    random.shuffle(numeric)
    group.s1 = numeric[0]
    group.s2 = numeric[1]
    group.s3 = numeric[2]
    group.s4 = numeric[3]
    group.s5 = numeric[4]

#    numeric = [0, 1, 2, 3, 4]
#    random.shuffle(numeric)
    group.c1 = numeric[0]
    group.c2 = numeric[1]
    group.c3 = numeric[2]
    group.c4 = numeric[3]
    group.c5 = numeric[4]


def set_results(group: Group):
    players = group.get_players()
    votes = [0 for i in range(0,2)]
    i=0
    for p in players:
        votes[i] = p.vote
        i=i+1
    print(votes)
    group.Collective_Choice = C.outcomes[votes[0]][votes[1]]

    for p in players:
        set_payoff(p)
#-----------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------
# player level
def set_MyPrefernces(player: Player):
    # determining the deterministic types:
#   preferences_list = [player.group.rank2*2-1, player.group.rank2*2, player.group.rank2*3-1, player.group.rank2*3]
    player.MyPreferences = random.randint(0,3)

def set_payoff(player: Player):
#    choice = player.group.Collective_Choice
    alt0 = player.group.rank1
    alt1 = player.group.rank2
    alt2 = player.group.rank3
    alts = [alt0, alt1, alt2]

    choice = alts[player.group.Collective_Choice]
    preferences_list = [player.group.rank2*2, player.group.rank2*2+1, player.group.rank3*2, player.group.rank3*2+1]
    j = preferences_list[player.MyPreferences]
    player.earnings = C.preferences[j][choice]
    
    if player.round_number == C.NUM_ROUNDS:
        p = player.in_round(player.subsession.paying_round)
        player.payoff = p.earnings
#-----------------------------------------------------------------------------------




#-----------------------------------------------------------------------------------
# PAGES
class SetupWaitPage(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def after_all_players_arrive(subsession):
        if subsession.round_number == 1:
            set_paying_round(subsession)
        players = subsession.get_players()
        for p in players: 
            set_MyPrefernces(p)
        groups = subsession.get_groups()
        for g in groups:
            set_ordering(g)

class Voting(Page):
    template_name = './Simple_NF_SS/Voting_GER.html'
    form_model = 'player'
    form_fields = ['vote']
    def vars_for_template(player):
        profile = player.MyPreferences+1
        preferences_list = [player.group.rank2*2, player.group.rank2*2+1, player.group.rank3*2, player.group.rank3*2+1]
        temp = [0 for x in range(0,4)]
        
#        print(profile)

        for i in range(0,4):
            j = preferences_list[i]
            temp[i] = [i+1, C.preferences[j][player.group.blue], C.preferences[j][player.group.green], C.preferences[j][player.group.orange]]

        alt0 = player.group.rank1
        alt1 = player.group.rank2
        alt2 = player.group.rank3
        alts = [alt0, alt1, alt2]
        strategies = [player.group.s1, player.group.s2, player.group.s3, player.group.s4, player.group.s5]
        context = [player.group.c1, player.group.c2, player.group.c3, player.group.c4, player.group.c5]

        outcomes0 = [0 for i in range(0,5)]
        outcomes1 = [0 for i in range(0,5)]
        outcomes2 = [0 for i in range(0,5)]
        outcomes3 = [0 for i in range(0,5)]
        outcomes4 = [0 for i in range(0,5)]

        for j in range(0,5):
            outcomes0[j] = alts[C.outcomes[strategies[0]][context[j]]]
            outcomes1[j] = alts[C.outcomes[strategies[1]][context[j]]]
            outcomes2[j] = alts[C.outcomes[strategies[2]][context[j]]]
            outcomes3[j] = alts[C.outcomes[strategies[3]][context[j]]]
            outcomes4[j] = alts[C.outcomes[strategies[4]][context[j]]]


        return dict(
            preference_profiles = temp,
            my_profile = profile,
            round_number = player.round_number,
            num_rounds = C.NUM_ROUNDS,
            blue = player.group.blue,
            green = player.group.green,
            orange = player.group.orange,
            rank1 = player.group.rank1,
            rank2 = player.group.rank2,
            rank3 = player.group.rank3,
            labels = C.LABELS,
            strats = strategies,
            outcomes0 = outcomes0,
            outcomes1 = outcomes1,
            outcomes2 = outcomes2,
            outcomes3 = outcomes3,
            outcomes4 = outcomes4,
            )

class VotingResultsWaitPage(WaitPage):
    wait_for_all_groups = False
    @staticmethod
    def after_all_players_arrive(group: Group):
        set_results(group)

class Results(Page):
    template_name = './Simple_NF_SS/Results_GER.html'
    def vars_for_template(player):
        if player.subsession.round_number == C.NUM_ROUNDS:
            p = player.in_round(player.subsession.paying_round)
            player.participant.vars['treatment_earnings'] = p.earnings

        profile = player.MyPreferences+1
        preferences_list = [player.group.rank2*2, player.group.rank2*2+1, player.group.rank3*2, player.group.rank3*2+1]
        temp = [0 for x in range(0,4)]

        alt0 = player.group.rank1
        alt1 = player.group.rank2
        alt2 = player.group.rank3
        alts = [alt0, alt1, alt2]

        Collective_Choice = alts[player.group.Collective_Choice]


        for i in range(0,4):
            j = preferences_list[i]
            temp[i] = [i+1, C.preferences[j][player.group.blue], C.preferences[j][player.group.green], C.preferences[j][player.group.orange]]

        return dict(
            preference_profiles = temp,
            my_profile = profile,
            round_number = player.round_number,
            num_rounds = C.NUM_ROUNDS,
            blue = player.group.blue,
            green = player.group.green,
            orange = player.group.orange,
            choice = Collective_Choice,
            rank1 = player.group.rank1,
            rank2 = player.group.rank2,
            rank3 = player.group.rank3,
            )
#-----------------------------------------------------------------------------------



#-----------------------------------------------------------------------------------
# PAGE SEQUENCE

page_sequence = [
                SetupWaitPage, 
                Voting,
                VotingResultsWaitPage,
                Results
                ]
#-----------------------------------------------------------------------------------









