from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'AA_control'
    PLAYERS_PER_GROUP = 1
    NUM_ROUNDS = 1
    task_time = 600

    # task parameters (matrix size):
    # y is universal
    all_y = 10 
    # x is type-specific
    blue_x = 10 
    red_x = 15


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    discriminated = models.IntegerField(min=0, max=1) # min = blue, max = red
    my_x = models.IntegerField(initial=10)
    my_y = models.IntegerField(initial=10)



# PAGES
class PracticeTask(Page):
    timeout_seconds = C.task_time

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            x = range(0,player.my_x),
            y = range(0,player.my_y)
            )




class ResultsWaitPage(WaitPage):
    pass


class Results(Page):
    pass


page_sequence = [
    PracticeTask
]
