from otree.api import *


doc = """
STATIC MECHANISM 1
t=2 interface
"""


class C(BaseConstants):
	NAME_IN_URL = 'SBC_S1_t2_'
	PLAYERS_PER_GROUP = None
	NUM_ROUNDS = 1


class Subsession(BaseSubsession):
	pass


class Group(BaseGroup):
	pass


class Player(BasePlayer):
	prolificID = models.StringField()

	test_variable = models.StringField()
#--------------------------------------------------------
# FUNCTIONS

def retrieve_data(player):
    import pandas as pd

    df = pd.read_csv('./_static/data.csv')
    prolificID = player.prolificID

    row = df.loc[df['prolificID'] == prolificID]

    test_variable = row['test_variable'].values
    print(test_variable)
    # Check if there is any data, then convert it to a string
    if test_variable.size > 0:  # Make sure the row isn't empty
        test_variable_str = str(test_variable[0])  # Get the first (and only) element as a string
        print(test_variable_str)  # This will print the string 'it damn worked'
        player.test_variable = test_variable_str  # Assign the string value to the player's test_variable
    else:
        print("No test_variable found for this player")




#--------------------------------------------------------
# PAGES
class LOGIN(Page):
	form_model = 'player'
	form_fields = ['prolificID'] 

	def before_next_page(player, timeout_happened):
		if player.round_number == 1:
			retrieve_data(player)

class TEST(Page):
   
   @staticmethod
   def is_displayed(player):
   	return player.round_number == 1

   @staticmethod
   def vars_for_template(player):
   	return dict(
   		prolificID = player.prolificID,
   		test_variable = player.test_variable
   		)



class ResultsWaitPage(WaitPage):
	pass


class Results(Page):
	pass


page_sequence = [LOGIN, TEST, Results]
