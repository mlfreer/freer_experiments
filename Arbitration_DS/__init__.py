from otree.api import *
import random
import math


doc = """
Application for simple arbitration experiment.
Case of dominant strategy mechanism.
"""

#-----------------------------------------------------------------------------------
# MODELS
#-----------------------------------------------------------------------------------
class C(BaseConstants):
	NAME_IN_URL = 'Arbitration_DS'
	PLAYERS_PER_GROUP = 2
	NUM_ROUNDS = 10

	preferences = [0 for i in range(0,6)]
	# defining the vector of preferences:
	preferences[0] = [20, 15, 2] # abc
	preferences[1] = [20, 2, 15] # acb
	preferences[2] = [15, 20, 2] # bac
	preferences[3] = [2, 20, 15] # bca
	preferences[4] = [15, 2, 20] # cab
	preferences[5] = [2, 15, 20] # cba

	alternatives = ['blue', 'green', 'orange'] #, 'purple']


class Subsession(BaseSubsession):
	paying_round = models.IntegerField(min=1,max=C.NUM_ROUNDS,initial=0)


class Group(BaseGroup):
	# variable to determine the group level preference ordering
	blue = models.IntegerField(min=0,max=2)
	green = models.IntegerField(min=0,max=2)
	orange = models.IntegerField(min=0,max=2)

	# default option:
	Default = models.IntegerField(min=0,max=3,initial=-1) 
	# current alternative:
	Alternative = models.IntegerField(min=0,max=3,initial=-1) 
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
	# Default:
	group.Default = 0
	# Alternative:
	group.Alternative = 1


def set_results(group: Group):
	players = group.get_players()
	votes = 0
	for p in players:
		votes = votes + p.vote

	if votes == 2:
		group.Collective_Choice = group.Alternative
	else:
		group.Collective_Choice = group.Default

	for p in players:
		set_payoff(p)
#-----------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------
# player level
def set_MyPrefernces(player: Player):
	# determining the deterministic types:
	player.MyPreferences = random.randint(0,5)

def set_payoff(player: Player):
	choice = player.group.Collective_Choice
	player.earnings = C.preferences[player.MyPreferences][choice]
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
	form_model = 'player'
	form_fields = ['vote']
	def vars_for_template(player):
		profile = player.MyPreferences+1
		temp = [0 for x in range(0,6)]
		for i in range(0,6):
			temp[i] = [i+1, C.preferences[i][player.group.blue], C.preferences[i][player.group.green], C.preferences[i][player.group.orange]]

		return dict(
			preference_profiles = temp,
			my_profile = profile,
			default = player.group.Default,
			alternative = player.group.Alternative,
			round_number = player.round_number,
			num_rounds = C.NUM_ROUNDS,
			blue = player.group.blue,
			green = player.group.green,
			orange = player.group.orange,
			)

class VotingResultsWaitPage(WaitPage):
    wait_for_all_groups = False
    @staticmethod
    def after_all_players_arrive(group: Group):
        set_results(group)

class Results(Page):
	def vars_for_template(player):
		profile = player.MyPreferences+1
		temp = [0 for x in range(0,6)]
		for i in range(0,6):
			temp[i] = [i+1, C.preferences[i][player.group.blue], C.preferences[i][player.group.green], C.preferences[i][player.group.orange]]

		return dict(
			preference_profiles = temp,
			my_profile = profile,
			default = player.group.Default,
			alternative = player.group.Alternative,
			round_number = player.round_number,
			num_rounds = C.NUM_ROUNDS,
			blue = player.group.blue,
			green = player.group.green,
			orange = player.group.orange,
			choice = player.group.Collective_Choice
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









