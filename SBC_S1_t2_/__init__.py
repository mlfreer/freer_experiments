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

	# test variabbles:
	q1 = models.StringField(label="Question 1")
	q2 = models.StringField(label="Question 2")
	q3 = models.StringField(label="Question 2")


#--------------------------------------------------------
# FUNCTIONS

def retrieve_data(player):
    import pandas as pd

    df = pd.read_csv('output.csv')
    prolificID = player.prolificID
    # once real replace with player.participant.label

    row = df.loc[df['prolificID'] == prolificID]

    #test_variable = row['test_variable'].values
    


#--------------------------------------------------------
# PAGES
class LOGIN(Page):
	form_model = 'player'
	form_fields = ['prolificID'] 

	def before_next_page(player, timeout_happened):
		if player.round_number == 1:
			retrieve_data(player)

# TEST PAGE WITH PROLIFIC ID
class TEST(Page):
   
   @staticmethod
   def is_displayed(player):
   	return player.round_number == 1

   @staticmethod
   def vars_for_template(player):
   	return dict(
   		prolificID = player.prolificID,
   		)


# PAGE WITH MULTIPLE STEPS (BACK AND FORTH BUTTON
class MultiStepPage(Page):
    form_model = 'player'
    form_fields = ['q1', 'q2', 'q3']  # all questions across steps

    def vars_for_template(self):
        return dict()



class ResultsWaitPage(WaitPage):
	pass


class Results(Page):
	pass


page_sequence = [LOGIN, TEST, MultiStepPage, Results]
