from otree.api import *
import pandas as pd
import os


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'SBC_S1_t1_'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

def save_to_csv(data_dict, filename="output.csv"):
    # Convert dict to DataFrame (1 row)
    df_new = pd.DataFrame([data_dict])

    # If file exists, append without header
    if os.path.exists(filename):
        df_new.to_csv(filename, mode="a", index=False, header=False)
    else:
        df_new.to_csv(filename, mode="w", index=False, header=True)

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


# PAGES
class MyPage(Page):
    def before_next_page(player, timeout_happened):
        if player.participant.label and player.participant.label.strip():
            save_to_csv({
                "prolificID": player.participant.label,
                # add other variables
            })


class ResultsWaitPage(WaitPage):
    pass


class Results(Page):
    pass


page_sequence = [MyPage, ResultsWaitPage, Results]
