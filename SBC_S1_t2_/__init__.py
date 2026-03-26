from otree.api import *


doc = """
STATIC MECHANISM 1
t=2 interface
"""


class C(BaseConstants):
	NAME_IN_URL = 'SBC_S1_t2_'
	PLAYERS_PER_GROUP = None
	NUM_ROUNDS = 15 

	ENDOWMENT = cu(14)
	# TREATMENT ORDER:
	# 0 = static, buy at t=1
	# 1 = static, buy at t=2
	# 2 = dynamic, option
	# 3 = dynamic, refund
#    PRICES_T1  = [[ 0 for i in range(15) ] for j in range(4)]
	PRICES_T1  = [[ 0 for i in range(11) ] for j in range(4)] # changing the parameters to the 11 period setup
    # outside is for treatment: 0 to 3
	PRICES_T1[0] = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
	PRICES_T1[2] = [8, 0, 0, 10, 2, 2, 4, 1, 1, 2, 3]
	PRICES_T1[3] = [8, 12, 10, 10, 12, 10, 10, 9, 10, 9, 10]
    #PRICES_T1[0] = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 8, 9, 11, 12]
    #PRICES_T1[2] = [8, 0, 0, 10, 1, 2, 1, 2, 3, 2, 3, 4, 7, 8, 9]
    #PRICES_T1[3] = [8, 12, 10, 10, 11, 12, 9, 10, 11, 8, 9, 10, 8, 9, 10]

    #PRICES_T2 = [[0 for i in range(15) ] for j in range(4)]
	PRICES_T2 = [[0 for i in range(11) ] for j in range(4)]
	PRICES_T1[1] = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
	PRICES_T2[2] = [0, 12, 10, 0, 10, 8, 6, 8, 9, 7, 7]
	PRICES_T2[3] = [0, 12, 10, 0, 10, 8, 6, 8, 9, 7, 7]
    #PRICES_T1[1] = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 8, 9, 11, 12]
    #PRICES_T2[2] = [0, 12, 10, 0, 10, 10, 8, 8, 8, 6, 6, 6, 1, 1, 1]
    #PRICES_T2[3] = [0, 12, 10, 0, 10, 10, 8, 8, 8, 6, 6, 6, 1, 1, 1]



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

	purchase_t1 = models.BooleanField(default=False)
	purchase_t2 = models.BooleanField(default=False)

	revised_purchase_t2 = models.BooleanField(default=False)
	
	price_t1 = models.IntegerField()
	price_t2 = models.IntegerField()

	earnings = models.IntegerField()

	selected_round = models.IntegerField()
	random_draw_1 = models.IntegerField()
	random_draw_2 = models.IntegerField()
	treatment = models.StringField()

	payoff_calculated = models.BooleanField(default=False)
	random_draws_generated = models.BooleanField(default=False)


#--------------------------------------------------------
# FUNCTIONS:
def draw_order(player: Player):
	session = player.session
	subsession = player.subsession
	participant = player.participant
	if (subsession.round_number == 1) or (participant.treatment==0):
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
	import random

	participant = player.participant
	label = participant.label
	if not label:
		return

	root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	csv_path = os.path.join(root_dir, 'output.csv')
	df = pd.read_csv(csv_path)
	#df = pd.read_csv("output.csv")
	print(df)

	if participant.treatment != 1:
		# assigning the prices:
		participant = player.participant
		subsession = player.subsession
	
		# retrieving prices:
		player.price_t1 = (participant.price_order_t1[subsession.round_number-1] )
		player.price_t2 = (participant.price_order_t2[subsession.round_number-1] )
		# retrieiving index:
		index = participant.indexes[subsession.round_number-1]
	
		# Coerce potentially malformed index values to numeric safely
		idx_series = pd.to_numeric(df['participant.indexes'], errors='coerce')
		rows = df[(df['participant.label'] == label)
				 & (df['player.price_t1'] == player.price_t1)
				 & (df['player.price_t2'] == player.price_t2)
				 & (idx_series == index)]
		print(rows, '\n', player.price_t1, '\n', participant.label, '\n', index)
		
		# check for the mistakes in the data set
		if rows.empty:
			print('Could not find matching row in output.csv for participant:', label)
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

		# recording the t=1 decision:
		player.purchase_t1 = bool( int( rows["player.revised_purchase"].squeeze() ) )
	else:
		player.random_draw_1 = int(participant.random_draw_1)
		player.random_draw_2 = int(participant.random_draw_2)



def select_random_round(player: Player):
	import random
	participant = player.participant
	subsession = player.subsession
	session = player.session

	# choosing the payment round
	selected_round = random.randint(1, C.NUM_ROUNDS)
	player.selected_round = selected_round
	
def compute_payoff(player: Player):
	if player.field_maybe_none('payoff_calculated'):
		return
	
	participant = player.participant
	subsession = player.subsession
	session = player.session

	# Initialize earnings to endowment in case no round matches
	endowment = int(C.ENDOWMENT)
	player.earnings = endowment
	
	print(f"Computing payoff for player, selected_round: {player.selected_round}")

	for p in player.in_all_rounds():
		retrieve_data(p)
#		print(f"Checking round {p.round_number} against selected {player.selected_round} , purchase_t1: {p.purchase_t1}, purchase_t2: {p.purchase_t2}")
		if p.round_number == player.selected_round:
			# determining the payoff
			x_draw = participant.x_draw
			a_bar = session.config['A_BAR']
			price_t1 = p.price_t1
			price_t2 = p.price_t2

			# determining if the ticket is won at t=1
			print(f"Round matched! random_draw_1: {p.random_draw_1}")
			won_t1 = (p.random_draw_1 == 1)
			won_t2 = (p.random_draw_2 == 1)

			if participant.treatment == 0:  # static, buy at t=1
				if p.purchase_t1:
					player.earnings = int(endowment - price_t1 + a_bar*won_t1 + x_draw*(1-won_t1) + a_bar*won_t2)
				else:
					player.earnings = int(endowment)
				print(f"Treatment 0 - purchase_t1: {p.purchase_t1}, earnings: {player.earnings}")

			elif participant.treatment == 1:  # static, buy at t=2
				if p.revised_purchase_t2:
					player.earnings = int(endowment - price_t2 + a_bar*won_t1 + x_draw*(1-won_t1) + a_bar*won_t2)
				else:
					player.earnings = int(endowment)
			elif participant.treatment == 2:  # dynamic, option
				if p.purchase_t1:
					if p.revised_purchase_t2:
						player.earnings = int(endowment - price_t1 - price_t2 + a_bar*won_t1 + x_draw*(1-won_t1) + a_bar*won_t2)
					else:
						player.earnings =  int(endowment - price_t1)
				else:
					player.earnings = int(endowment)
			elif participant.treatment == 3:  # dynamic, refund
				if p.purchase_t1:
					if p.revised_purchase_t2==0:
						player.earnings = int(endowment - price_t1 + a_bar*won_t1 + x_draw*(1-won_t1) + a_bar*won_t2)
					else:
						player.earnings = int(endowment - price_t1 + price_t2)
				else:
					player.earnings = int(endowment)
			
			print(f"Final earnings set to: {player.earnings}")
			player.payoff_calculated = True # marking the fact that payoff is calculated
			break  # Found the selected round, no need to continue

#--------------------------------------------------------
# PAGES

# TEST PAGE WITH PROLIFIC ID
class ExperimentStarts(Page):

	@staticmethod
	def is_displayed(player):
		if player.participant.treatment != 0:
			return player.subsession.round_number == 1
		else:
			return player.subsession.round_number == C.NUM_ROUNDS

	@staticmethod
	def before_next_page(player, timeout_happened):
		# comptuing payoff at the start of the experiment if the treatment is static, buy at t=1
		if player.participant.treatment == 0:
			retrieve_data(player)
			select_random_round(player)
			compute_payoff(player)		

	@staticmethod
	def vars_for_template(player):
		participant = player.participant
		session = player.session
		# Load data from stage t1 before drawing any new order.
		draw_order(player)
		retrieve_data(player)
		
		# Calculate example_sum for instructions
		a_bar = session.config['A_BAR']
		x_draw = participant.x_draw
		example_sum = x_draw + a_bar
		
		result = 'heads' if player.random_draw_1 == 1 else 'tails'

		return dict(
			treatment=participant.treatment,
			x_draw=x_draw,
			example_sum=example_sum,
			coin_result=result
		)


# PAGE WITH MULTIPLE STEPS (BACK AND FORTH BUTTON
class Decision(Page):
	form_model = 'player'
	form_fields = ['purchase_t2']
	@staticmethod
	def is_displayed(player: Player):
		session = player.session
		subsession = player.subsession
		participant = player.participant
		if participant.treatment != 0:
			player.price_t1 = (participant.price_order_t1[subsession.round_number-1] )
			player.price_t2 = ( participant.price_order_t2[subsession.round_number-1] )
		x_draw = participant.x_draw # temp variable for x_draw
		return participant.treatment != 0
	
	@staticmethod
	def vars_for_template(player: Player):
		# recovering the data:
		retrieve_data(player)
		
		# Calculate example_sum for instructions
		participant = player.participant
		session = player.session
		a_bar = session.config['A_BAR']
		x_draw = participant.x_draw
		example_sum = x_draw + a_bar

		return dict(
			price_t1=player.price_t1,
			price_t2=player.price_t2,
			x_draw=x_draw,
			example_sum=example_sum,
		)
	
	@staticmethod
	def before_next_page(player: Player, timeout_happened):
		player.revised_purchase_t2 = player.purchase_t2
		
		# temporary removing to compute the payoffs after the revision page
#		if player.subsession.round_number == C.NUM_ROUNDS:
#			select_random_round(player)
#			compute_payoff(player)


# REVISION PAGE
class RevisionPage(Page):
    form_model = 'player'

    @staticmethod
    def is_displayed(player: Player):
        return (player.subsession.round_number == C.NUM_ROUNDS) and (player.participant.treatment != 0)

    @staticmethod
    def live_method(player: Player, data: dict):
        round_num = data['round']          # which round's decision is being revised
        revised = data['revised_purchase'] # the new True/False value
        player.in_round(round_num).revised_purchase_t2 = revised  # writes to that round's player object

    @staticmethod
    def vars_for_template(player: Player):
        past = []
        for r in range(1, C.NUM_ROUNDS + 1):
            p = player.in_round(r)
            past.append(dict(
                round=r,
                price_t1=p.price_t1,
                price_t2=p.price_t2,
                purchase_t2=p.purchase_t2,
                revised_purchase_t2=p.revised_purchase_t2,
            ))
        return dict(past_decisions=past)

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.subsession.round_number == C.NUM_ROUNDS:
            select_random_round(player)
            compute_payoff(player)



class Results(Page):
	@staticmethod
	def is_displayed(player):
		# For treatment 0: show results on round 1 (after ExperimentStarts)
		# For other treatments: show results on final round (after all decisions)
		return player.subsession.round_number == C.NUM_ROUNDS
	
	@staticmethod
	def vars_for_template(player: Player):
		participant = player.participant
		session = player.session
		

		selected_player = player.in_round(player.selected_round)
		retrieve_data(selected_player)
		compute_payoff(player)

		# recording the payoff in the end:
		player.payoff = player.earnings
		
		return dict(
			selected_round=player.selected_round,
			payoff=player.field_maybe_none('earnings'),
			price_t1=selected_player.price_t1,
			price_t2=selected_player.price_t2,
			purchase_t1=selected_player.field_maybe_none('purchase_t1'),
			purchase_t2=selected_player.field_maybe_none('revised_purchase_t2'),
			random_draw_1=selected_player.field_maybe_none('random_draw_1'),
			random_draw_2=selected_player.field_maybe_none('random_draw_2'),
			x_draw=participant.x_draw,
			a_bar=session.config['A_BAR'],
			treatment=participant.treatment,
#			completion_url=session.config['completion_url'],
		)
	


page_sequence = [
	ExperimentStarts, 
	Decision, 
	RevisionPage,
	Results]
