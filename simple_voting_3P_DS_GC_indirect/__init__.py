from otree.api import *
import random
import math


doc = """
Your app description
"""

class Constants(BaseConstants):
    name_in_url = 'DSVotingU'
    players_per_group = 3

    num_rounds = 10 # number of periods to be set to 10

    type_probability = .5 # probability of type of 2 and 3 being (a)

    preferences = [0 for i in range(0,4)]
    # defining the vector of preferences:
    preferences[0] = [20, 15, 2] # player 1
    preferences[1] = [15, 20, 2] # player 2a
    preferences[2] = [2, 20, 15] # player 2b
    preferences[3] = [2, 15, 20] # player 4

    alternatives = ['blue', 'green', 'orange'] #, 'purple']

#-----------------------------------------------------------------------------------
# Models
#-----------------------------------------------------------------------------------
class Subsession(BaseSubsession):
    # variable to determine the group level preference ordering
    blue = models.IntegerField(min=0,max=2)
    green = models.IntegerField(min=0,max=2)
    orange = models.IntegerField(min=0,max=2)

    # variables for paying round:
    paying_round = models.IntegerField(min=1,max=Constants.num_rounds,initial=0)
    

class Group(BaseGroup):
    # variable to determine the group level preference ordering
    blue = models.IntegerField(min=0,max=2)
    green = models.IntegerField(min=0,max=2)
    orange = models.IntegerField(min=0,max=2)

    Option1 = models.IntegerField(min=1,max=4,initial=0)
    Option2 = models.IntegerField(min=1,max=4,initial=0)
    t1_Eliminated = models.IntegerField(min=1,max=4,initial=0)
    t2_Eliminated = models.IntegerField(min=1,max=4,initial=0)

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
def set_order(session: Subsession):
    numeric = [0, 1, 2]
    random.shuffle(numeric)
    session.blue = numeric[0]
    session.green = numeric[1]
    session.orange = numeric[2]

def creating_session(session: Subsession):
    session.group_randomly(fixed_id_in_group=False)

def set_paying_round(session: Subsession):
    p_round = random.randint(1,Constants.num_rounds)
    s = session.in_round(Constants.num_rounds)
    s.paying_round = p_round

#-----------------------------------------------------------------------------------
# group level
def set_ordering(group: Group):
    group.blue = group.subsession.blue
    group.green = group.subsession.green
    group.orange = group.subsession.orange

def t1_elimination(group: Group):
    numeric_alternatives = [1, 2, 3]
    random.shuffle(numeric_alternatives)
    remaining = [numeric_alternatives[0], numeric_alternatives[1]]
    remaining.sort()

    eliminated = numeric_alternatives[2]
#    eliminated.sort()

    group.Option1 = remaining[0]
    group.Option2 = remaining[1]
    group.t1_Eliminated = eliminated


def set_results(group: Group):
    players = group.get_players()
    votes = [0 for x in range(0,3)]
    # computing the votes
    for p in players:
        votes[p.vote-1] = votes[p.vote-1]+1

    # finding eliminated alternative
    max_element = max(votes)    
    group.t2_Eliminated = votes.index(max(votes))

    # computing the collective choice
    if group.t2_Eliminated == group.Option1-1:
        group.Collective_Choice = group.Option2-1
    else:
        group.Collective_Choice = group.Option1-1

    players = group.get_players()
    for p in players:
        p.set_payoff()

#-----------------------------------------------------------------------------------
# player level
def set_MyPrefernces(player: Player):
    # determining the deterministic types:
    if player.id_in_group == 1:
        player.MyPreferences = 0 
    if player.id_in_group == 3:
        player.MyPreferences = 3
    # determining the stochastic types:
    if player.id_in_group == 2:
        r = random.uniform(0,1)
        if r<=Constants.type_probability:
            player.MyPreferences = 1
        else:
            player.MyPreferences = 2

def set_payoff(player: Player):
    choice = player.group.Collective_Choice
    player.earnings = Constants.preferences[player.group.Ordering][player.MyPreferences][choice]
    if player.subsession.round_number == Constants.nusm_rounds:
        p = player.in_round(player.subsession.paying_round)
        player.payoff = p.earnings

#-----------------------------------------------------------------------------------
# PAGES
#-----------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------
# voting treatment page:
class SetupWaitPage(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def after_all_players_arrive(subsession):
        if subsession.round_number == 1:
            set_paying_round(subsession)
        players = subsession.get_players()
        set_order(subsession)
        for p in players: 
            set_MyPrefernces(p)
        groups = subsession.get_groups()
        for g in groups:
            set_ordering(g)
            t1_elimination(g)

class Voting(Page):
    form_model = 'player'
    form_fields = ['vote']
    def vars_for_template(player):
        profile = player.MyPreferences
        temp = [0 for x in range(0,4)]
        temp[0] = [ Constants.preferences[0][player.group.blue], Constants.preferences[0][player.group.green], Constants.preferences[0][player.group.orange]]
        temp[1] = [ Constants.preferences[1][player.group.blue], Constants.preferences[1][player.group.green], Constants.preferences[1][player.group.orange]]
        temp[2] = [ Constants.preferences[2][player.group.blue], Constants.preferences[2][player.group.green], Constants.preferences[2][player.group.orange]]
        temp[3] = [ Constants.preferences[3][player.group.blue], Constants.preferences[3][player.group.green], Constants.preferences[3][player.group.orange]]

#        temp[1] = Constants.preferences[player.group.Ordering][profile][1]
#        temp[2] = Constants.preferences[player.group.Ordering][profile][2]
#        temp[3] = Constants.preferences[player.group.Ordering][profile][3]

        return dict(
            preference_profiles = temp,
            my_number = player.id_in_group,
#            my_preferences = temp,
            my_profile = profile,
            numeric_options = [player.group.Option1, player.group.Option2],
            options = [Constants.alternatives[player.group.Option1-1],Constants.alternatives[player.group.Option2-1]],
            eliminated = Constants.alternatives[player.group.t1_Eliminated-1],
            round_number = player.round_number,
            num_rounds = Constants.num_rounds
            )

class ResultsWaitPage(WaitPage):
    wait_for_all_groups = False
    def after_all_players_arrive(player):
        player.group.set_results()

class Results(Page):
    def vars_for_template(player):
        if player.player.subsession.round_number == Constants.num_rounds:
            p = player.in_round(player.player.subsession.paying_round)
            player.participant.vars['treatment_earnings'] = p.earnings

        temp1 = [0 for x in range(0,4)]
        profile = self.player.MyPreferences
        temp1[0] = Constants.preferences[player.group.Ordering][profile][0]
        temp1[1] = Constants.preferences[player.group.Ordering][profile][1]
        temp1[2] = Constants.preferences[player.group.Ordering][profile][2]
        temp1[3] = Constants.preferences[player.group.Ordering][profile][3]


        return dict(
            my_preferences = temp1,
            preference_profiles = Constants.preferences[self.player.group.Ordering],
            my_number = player.id_in_group,
            my_profile = profile,
            collective_choice = Constants.alternatives[self.player.group.Collective_Choice],
            numeric_collective_choice = self.player.group.Collective_Choice,
            earnings = temp1[self.player.group.Collective_Choice],
            round_number = self.player.subsession.round_number,
            num_rounds = Constants.num_rounds
            )

page_sequence = [
                # voting treatment
                SetupWaitPage,
                Voting,
                ResultsWaitPage,
                Results,
                ]
    


    
