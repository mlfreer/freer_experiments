from otree.api import *
import random
import math


doc = """
Your app description
"""

class Constants(BaseConstants):
    name_in_url = '3P_MAJ_GC_indirect'
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
    # variables for paying round:
    paying_round = models.IntegerField(min=1,max=Constants.num_rounds,initial=0)
    

class Group(BaseGroup):
    # variable to determine the group level preference ordering
    blue = models.IntegerField(min=0,max=2)
    green = models.IntegerField(min=0,max=2)
    orange = models.IntegerField(min=0,max=2)

    Option1 = models.IntegerField(min=0,max=3,initial=0)
    Option2 = models.IntegerField(min=0,max=3,initial=0)
    Option3 = models.IntegerField(min=0,max=3,initial=0)

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
    p_round = random.randint(1,Constants.num_rounds)
    s = session.in_round(Constants.num_rounds)
    s.paying_round = p_round

#-----------------------------------------------------------------------------------
# group level
def set_ordering(group: Group):
    numeric = [0, 1, 2]
    random.shuffle(numeric)
    group.blue = numeric[0]
    group.green = numeric[1]
    group.orange = numeric[2]

    # initializing options:
    group.Option1 = 0
    group.Option2 = 1
    group.Option3 = 2

def set_results(group: Group):
    players = group.get_players()
    votes = [0 for x in range(0,3)]
    # computing the votes
    for p in players:
        votes[p.vote] = votes[p.vote]+1

    # finding eliminated alternative
    max_element = max(votes)    
    if max_element == 1:
        r=random.randint(0,2)
        group.Collective_Choice=r
    else:
        group.Collective_Choice = votes.index(max(votes))
    for p in players:
        set_payoff(p)

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
    blue = player.group.blue
    green = player.group.green
    orange = player.group.orange
    if choice == 0:
        player.earnings = Constants.preferences[player.MyPreferences][blue]
    elif choice == 1:
        player.earnings = Constants.preferences[player.MyPreferences][green]
    elif choice == 2:
        player.earnings = Constants.preferences[player.MyPreferences][orange]
    if player.round_number == Constants.num_rounds:
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
        for p in players: 
            set_MyPrefernces(p)
        groups = subsession.get_groups()
        for g in groups:
            set_ordering(g)

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
            numeric_options = [player.group.Option1, player.group.Option2, player.group.Option3],
            options = [Constants.alternatives[player.group.Option1],Constants.alternatives[player.group.Option2], Constants.alternatives[player.group.Option3] ],
            round_number = player.round_number,
            num_rounds = Constants.num_rounds
            )

class ResultsWaitPage(WaitPage):
    wait_for_all_groups = False
    @staticmethod
    def after_all_players_arrive(group: Group):
        set_results(group)

class Results(Page):
    def vars_for_template(player):
        if player.subsession.round_number == Constants.num_rounds:
            p = player.in_round(player.subsession.paying_round)
            player.participant.vars['treatment_earnings'] = p.earnings

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
            choice = player.group.Collective_Choice,
            earnings = player.earnings,
#            my_preferences = temp,
            my_profile = profile,
            round_number = player.round_number,
            num_rounds = Constants.num_rounds
            )

page_sequence = [
                # voting treatment
                SetupWaitPage,
                Voting,
                ResultsWaitPage,
                Results,
                ]
    


    
