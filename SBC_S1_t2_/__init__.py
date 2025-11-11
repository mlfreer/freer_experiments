from otree.api import *


doc = """
STATIC MECHANISM 1
t=2 interface
"""


class C(BaseConstants):
	NAME_IN_URL = 'SBC_S1_t2_'
	PLAYERS_PER_GROUP = None
	NUM_ROUNDS = 2

	ENDOWMENT = cu(15)
	# TREATMENT ORDER:
	# 0 = static, buy at t=1
	# 1 = static, buy at t=2
	# 2 = dynamic, option
	# 3 = dynamic, refund
	PRICES_T1  = [[ 0 for i in range(15) ] for j in range(4)]
	# outside is for treatment: 0 to 3
	PRICES_T1[0] = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 8, 9, 11, 12]
	PRICES_T1[2] = [8, 0, 0, 10, 1, 2, 1, 2, 3, 2, 3, 4, 7, 8, 9]
	PRICES_T1[3] = [8, 12, 10, 10, 11, 12, 9, 10, 11, 8, 9, 10, 8, 9, 10]

	PRICES_T2 = [[0 for i in range(15) ] for j in range(4)]
	PRICES_T1[1] = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 8, 9, 11, 12]
	PRICES_T2[2] = [0, 12, 10, 0, 10, 10, 8, 8, 8, 6, 6, 6, 1, 1, 1]
	PRICES_T2[3] = [0, 12, 10, 0, 10, 10, 8, 8, 8, 6, 6, 6, 1, 1, 1]



class Subsession(BaseSubsession):
	pass


class Group(BaseGroup):
	pass

 
class Player(BasePlayer):
	#prolificID = models.StringField()	
	# test variabbles:
	q1 = models.StringField(label="Question 1")
	q2 = models.StringField(label="Question 2")
	q3 = models.StringField(label="Question 2")

	purchase = models.BooleanField(choices=[[True, 'Yes'], [False, 'No']], widget=widgets.RadioSelectHorizontal, label='')#, label='Do you want to purchase this lottery ticket?', )
	
	price_t1 = models.IntegerField()
	price_t2 = models.IntegerField()

	selected_round = models.IntegerField()
	random_draw_1 = models.IntegerField()
	random_draw_2 = models.IntegerField()
	treatment = models.StringField()


#--------------------------------------------------------
# FUNCTIONS:
def draw_order(player: Player):
	session = player.session
	subsession = player.subsession
	participant = player.participant
	if subsession.round_number == 1:
		import random
		indexes = list( range(len(C.PRICES_T1[participant.treatment])) )
		random.shuffle(indexes)

		pricelist_t1 = list( [C.PRICES_T1[participant.treatment][j] for j in indexes ] )
		pricelist_t2 = list( [C.PRICES_T2[participant.treatment][j] for j in indexes ] )
		participant.price_order_t1 = pricelist_t1
		participant.price_order_t2 = pricelist_t2
		participant.indexes = indexes


def retrieve_data(player):
	"""Load only the single 'appropriate' row for this participant from output.csv.

	Assumptions:
	  - output.csv exists in project root (one level up from this app folder)
	  - One row was written per round in stage t1 for each participant
	  - Columns present (no missing values):
		  participant.label, participant.x_draw, participant.treatment, round_number (optional)
	Selection rule:
	  - If round_number column exists: take the row with the largest round_number (latest round)
	  - Otherwise: take the last matching row as it appears in the file
	"""
	import pandas as pd
	import os

	participant = player.participant
	label = participant.label
	if not label:
		return

	root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	csv_path = os.path.join(root_dir, 'output.csv')
	df = pd.read_csv(csv_path)

	# assigning the prices:
	participant = player.participant
	subsession = player.subsession
	
	# retrieving prices:
	player.price_t1 = (participant.price_order_t1[subsession.round_number-1] )
	player.price_t2 = ( participant.price_order_t2[subsession.round_number-1] )
	# retrieiving index:
	index = participant.indexes[subsession.round_number-1]
	
	rows = df[(df['participant.label'] == label) & (df['player.price_t1'] == player.price_t1) & (df['player.price_t2'] == player.price_t2) & (df['participant.indexes'].astype(int) == index)]
	print(rows, '\n', player.price_t1, '\n', participant.label, '\n', index)
	if rows.empty:
		return  # nothing recorded for this label
	
	print(rows["player.random_draw_1"].squeeze().astype(int))

	# recording random_draw_1
	temp = float(rows["player.random_draw_1"].squeeze())
	temp = int(temp)
	player.random_draw_1 = temp

	#recording random draw 2
	temp = float(rows["player.random_draw_2"].squeeze())
	temp = int(temp)
	player.random_draw_2 = temp
	#player.random_draw_1 = rows["player.random_draw_1"].squeeze().astype(int)

	


#--------------------------------------------------------
# PAGES

# TEST PAGE WITH PROLIFIC ID
class ExperimentStarts(Page):

	@staticmethod
	def is_displayed(player):
		return player.round_number == 1

	@staticmethod
	def before_next_page(player, timeout_happened):
		# Load data from stage t1 before drawing any new order.
		draw_order(player)
		retrieve_data(player)
		

	@staticmethod
	def vars_for_template(player):
		participant = player.participant
		return dict(
			treatment=participant.treatment,
			x_draw=participant.x_draw,
		)


# PAGE WITH MULTIPLE STEPS (BACK AND FORTH BUTTON
class Decision(Page):
	form_model = 'player'
	form_fields = ['purchase']
	@staticmethod
	def is_displayed(player: Player):
		session = player.session
		subsession = player.subsession
		participant = player.participant
		player.price_t1 = (participant.price_order_t1[subsession.round_number-1] )
		player.price_t2 = ( participant.price_order_t2[subsession.round_number-1] )
		x_draw = participant.x_draw # temp variable for x_draw
		return participant.treatment != 1
	
	@staticmethod
	def vars_for_template(player: Player):
		# recovering the data:
		retrieve_data(player)

		return dict(
			price_t1=player.price_t1,
			price_t2=player.price_t2,
			x_draw=player.participant.x_draw,
		)

class ResultsWaitPage(WaitPage):
	def is_displayed(player):
		return player.round_number == C.NUM_ROUNDS


class Results(Page):
	def is_displayed(player):
		return player.round_number == C.NUM_ROUNDS


page_sequence = [
	ExperimentStarts, 
	Decision, 
	Results]
