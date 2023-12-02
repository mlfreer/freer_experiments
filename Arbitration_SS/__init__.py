from otree.api import *
import random
import math


doc = """
Application for simple arbitration experiment.
Case of strategically simple mechanism.
"""

#-----------------------------------------------------------------------------------
# MODELS
#-----------------------------------------------------------------------------------
class C(BaseConstants):
	NAME_IN_URL = 'Arbitration_SS'
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

	# default option:
	Default_t1 = models.IntegerField(min=0,max=3,initial=-1) 
	Default_t2 = models.IntegerField(min=0,max=3,initial=-1) 
	# current alternative:
	Alternative_t1 = models.IntegerField(min=0,max=3,initial=-1) 
	Alternative_t2 = models.IntegerField(min=0,max=3,initial=-1) 
	# final choice
	Collective_Choice = models.IntegerField(min=0,max=3,initial=-1)
	


class Player(BasePlayer):
	# variable to store the type:
	MyPreferences = models.IntegerField(min=-1, max=3, initial=-1)

	# variable to store the voting:
	vote_t1  = models.IntegerField(min=0,max=4)
	vote_t2  = models.IntegerField(min=0,max=4)
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

	options = [0, 1, 2]
	random.shuffle(options)
	# Default:
	group.Default_t1 = options[0]
	group.Default_t2 = options[0]
	# Alternative:
	group.Alternative_t1 = options[1]
	group.Alternative_t2 = options[2]

	# Recording the ranking
	group.rank1 = options[0]
	group.rank2 = options[1]
	group.rank3 = options[2]


def set_t2(group: Group):
	players = group.get_players()
	votes = 0
	for p in players:
		votes = votes + p.vote_t1
	if votes == 2:
		group.Default_t2 = group.Alternative_t1


def set_results(group: Group):
	players = group.get_players()
	votes = 0
	for p in players:
		votes = votes + p.vote_t2

	if votes == 2:
		group.Collective_Choice = group.Alternative_t2
	else:
		group.Collective_Choice = group.Default_t2

	for p in players:
		set_payoff(p)
#-----------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------
# player level
def set_MyPrefernces(player: Player):
	# determining the deterministic types:
	player.MyPreferences = random.randint(0,3)

def set_payoff(player: Player):
	choice = player.group.Collective_Choice
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

class Voting_t1(Page):
	template_name = './Arbitration_SS/Voting_t1_DE.html'
	form_model = 'player'
	form_fields = ['vote_t1']
	def vars_for_template(player):
		profile = player.MyPreferences+1
		print(profile)
		preferences_list = [player.group.rank2*2, player.group.rank2*2+1, player.group.rank3*2, player.group.rank3*2+1]
		temp = [0 for x in range(0,4)]
		for i in range(0,4):
			j = preferences_list[i]
			temp[i] = [i+1, C.preferences[j][player.group.blue], C.preferences[j][player.group.green], C.preferences[j][player.group.orange]]

		return dict(
			preference_profiles = temp,
			my_profile = profile,
			default = player.group.Default_t1,
			alternative = player.group.Alternative_t1,
			round_number = player.round_number,
			num_rounds = C.NUM_ROUNDS,
			blue = player.group.blue,
			green = player.group.green,
			orange = player.group.orange,
			rank1 = player.group.rank1,
			rank2 = player.group.rank2,
			rank3 = player.group.rank3,
			)

class Voting_t1_ResultsWaitPage(WaitPage):
	wait_for_all_groups = False
	@staticmethod
	def after_all_players_arrive(group: Group):
		set_t2(group)

class Voting_t2(Page):
	template_name = './Arbitration_SS/Voting_t2_DE.html'
	form_model = 'player'
	form_fields = ['vote_t2']
	def vars_for_template(player):
		profile = player.MyPreferences+1
		preferences_list = [player.group.rank2*2, player.group.rank2*2+1, player.group.rank3*2, player.group.rank3*2+1]
		temp = [0 for x in range(0,4)]

		for i in range(0,4):
			j = preferences_list[i]
			temp[i] = [i+1, C.preferences[j][player.group.blue], C.preferences[j][player.group.green], C.preferences[j][player.group.orange]]

		return dict(
			preference_profiles = temp,
			my_profile = profile,
			default = player.group.Default_t2,
			alternative = player.group.Alternative_t2,
			round_number = player.round_number,
			num_rounds = C.NUM_ROUNDS,
			blue = player.group.blue,
			green = player.group.green,
			orange = player.group.orange,
			rank1 = player.group.rank1,
			rank2 = player.group.rank2,
			rank3 = player.group.rank3,
			)

class Voting_t2_ResultsWaitPage(WaitPage):
	wait_for_all_groups = False
	@staticmethod
	def after_all_players_arrive(group: Group):
		set_results(group)


class Results(Page):	
	template_name = './Arbitration_SS/Results_DE.html'
			
	def vars_for_template(player):
		if player.subsession.round_number == C.NUM_ROUNDS:
			p = player.in_round(player.subsession.paying_round)
			player.participant.vars['treatment_earnings'] = p.earnings

		

		profile = player.MyPreferences+1
		preferences_list = [player.group.rank2*2, player.group.rank2*2+1, player.group.rank3*2, player.group.rank3*2+1]
		temp = [0 for x in range(0,4)]
		print(preferences_list[3])
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
			choice = player.group.Collective_Choice,
			rank1 = player.group.rank1,
			rank2 = player.group.rank2,
			rank3 = player.group.rank3,
			)
#-----------------------------------------------------------------------------------



#-----------------------------------------------------------------------------------
# PAGE SEQUENCE

page_sequence = [
				SetupWaitPage, 
				Voting_t1,
				Voting_t1_ResultsWaitPage,
				Voting_t2,
				Voting_t2_ResultsWaitPage,
				Results
				]
#-----------------------------------------------------------------------------------









