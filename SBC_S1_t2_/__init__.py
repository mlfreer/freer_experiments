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
	#prolificID = models.StringField()	
	# test variabbles:
	q1 = models.StringField(label="Question 1")
	q2 = models.StringField(label="Question 2")
	q3 = models.StringField(label="Question 2")


#--------------------------------------------------------
# FUNCTIONS

def retrieve_data(player):
    import pandas as pd
    import os

    # Use absolute path to find output.csv in project root
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(root_dir, 'output.csv')
    
    df = pd.read_csv(csv_path)

    # Find the matching row for this participant
    row = df.loc[df['participant.label'] == player.participant.label].iloc[0]
    
    # Set participant variables from the data
    player.participant.x_draw = float(row['participant.x_draw'])
    player.participant.treatment = int(row['participant.treatment'])
    


#--------------------------------------------------------
# PAGES

# TEST PAGE WITH PROLIFIC ID
class TEST(Page):
   
   @staticmethod
   def is_displayed(player):
   	return player.round_number == 1

   @staticmethod
   def vars_for_template(player):
	   participant = player.participant
	   return dict(
   			treatment= participant.treatment,
			x_draw= participant.x_draw,   		
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


page_sequence = [
	TEST, 
	MultiStepPage, 
	Results]
