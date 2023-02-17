from otree.api import *
import random
import math


doc = """
Your app description
"""

class Constants(BaseConstants):
    name_in_url = 'DSVotingU'
    players_per_group = 4

    num_rounds = 10 # number of periods to be set to 10

    type_probability = .5 # probability of type of 2 and 3 being (a)

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
    Eliminated1 = models.IntegerField(min=1,max=4,initial=0)

    Collective_Choice = models.IntegerField(min=0,max=3,initial=-1)
    


class Player(BasePlayer):
    # variable to store the type:
    MyPreferences = models.IntegerField(min=-1, max=3, initial=-1)

    def set_MyPrefernces(self):
        # determining the deterministic types:
        if self.id_in_group == 1:
            self.MyPreferences = 0 
        if self.id_in_group == 3:
            self.MyPreferences = 3
        # determining the stochastic types:
        if self.id_in_group == 2:
            r = random.uniform(0,1)
            if r<=Constants.type_probability:
                self.MyPreferences = 1
            else:
                self.MyPreferences = 2

    # variable to store the voting:
    vote  = models.IntegerField(min=0,max=4)
    earnings = models.IntegerField(min=0,max=20)

    # Setting payoffs for the voting treatment:
    def set_payoff(self):
        choice = self.group.Collective_Choice
        self.earnings = Constants.preferences[self.group.Ordering][self.MyPreferences][choice]
        if self.subsession.round_number == Constants.nusm_rounds:
            p = self.in_round(self.subsession.paying_round)
            self.payoff = p.earnings


#-----------------------------------------------------------------------------------
# FUNCTIONS
#-----------------------------------------------------------------------------------
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
def set_ordering(group: Group):
    group.blue = group.subsession.blue
    group.green = group.subsession.green
    group.orange = group.subsession.orange

def eliminate_alternatives(group: Group):
    numeric_alternatives = [1, 2, 3, 4]
    random.shuffle(numeric_alternatives)
    remaining = [numeric_alternatives[0], numeric_alternatives[1]]
    remaining.sort()

    eliminated = [numeric_alternatives[2], numeric_alternatives[3]]
    eliminated.sort()


    group.Option1 = remaining[0]
    group.Option2 = remaining[1]
    group.Eliminated1 = eliminated[0]
    group.Eliminated2 = eliminated[1]

def set_results(group: Group):
    players = group.get_players()
    votes = [0 for x in range(0,4)]
    for p in players:
        votes[p.vote-1] = votes[p.vote-1]+1

    # checking whether the maximum is unique
    count = 0
    max_element = max(votes)
    for x in votes:
        if x >= max_element:
            count = count+1

    if count > 1:
        r = random.uniform(0,1)
        if r<=.5:
            group.stage3_Eliminated = group.Option1-1
        else:
            group.stage3_Eliminated = group.Option2-1
    else:
        group.stage3_Eliminated = votes.index(max(votes))

    if group.stage3_Eliminated == group.Option1-1:
        group.Collective_Choice = group.Option2-1
    else:
        group.Collective_Choice = group.Option1-1

    players = group.get_players()
    for p in players:
        p.set_payoff()
#-----------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------
# PAGES
#-----------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------
# voting treatment page:
class SetupWaitPage(WaitPage):
    wait_for_all_groups = True
    def after_all_players_arrive(player):
        if player.subsession.round_number == 1:
            player.subsession.set_paying_round()
        players = player.subsession.get_players()
        player.subsession.set_order()
        for p in players: 
            p.set_MyPrefernces()
        groups = player.subsession.get_groups()
        for g in groups:
            g.set_ordering()
            g.eliminate_alternatives()

class Voting(Page):
    form_model = 'player'
    form_fields = ['vote']
    def vars_for_template(player):
        profile = player.MyPreferences
        temp = [0 for x in range(0,4)]
        temp[0] = Constants.preferences[player.group.Ordering][profile][0]
        temp[1] = Constants.preferences[player.group.Ordering][profile][1]
        temp[2] = Constants.preferences[player.group.Ordering][profile][2]
        temp[3] = Constants.preferences[player.group.Ordering][profile][3]

        return dict(
            preference_profiles = Constants.preferences[self.player.group.Ordering],
            my_number = player.id_in_group,
            my_preferences = temp,
            my_profile = profile,
            numeric_options = [self.group.Option1, self.group.Option2],
            options = [Constants.alternatives[self.group.Option1-1],Constants.alternatives[self.group.Option2-1]],
            eliminated = [Constants.alternatives[self.group.Eliminated1-1],Constants.alternatives[self.group.Eliminated2-1]],
            round_number = self.player.subsession.round_number,
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
    


    
