import time
import json
from random_username.generate import generate_username

from otree import settings
from otree.api import *
import random

from _static import task_sliders
#from _static import encode_image
from _static.image_utils import encode_image

doc = """
"""


class Constants(BaseConstants):
    name_in_url = "CC_NV_PAM"
    players_per_group = 4
    num_rounds = 15

    task_time = 60



class Subsession(BaseSubsession):
    paying_round = models.IntegerField(min=1,max=Constants.num_rounds,initial=0)


#------------------------------------------------------------------
def creating_session(subsession: Subsession):
    session = subsession.session
    defaults = dict(
        trial_delay=1.0,
        retry_delay=0.1,
        num_sliders=50,
        num_columns=2,
        attempts_per_slider=100
    )
    session.params = {}
    for param in defaults:
        session.params[param] = session.config.get(param, defaults[param])

#    for p in subsession.get_players():
#        temp = generate_username(1)
#        print(temp[0])
#        p.user_name = temp[0]
#        p.user_name = temp

def set_paying_round(session: Subsession):
    p_round = random.randint(1,Constants.num_rounds)
    s = session.in_round(Constants.num_rounds)
    s.paying_round = p_round

def set_groups(subsession: Subsession):
    players = subsession.get_players()

    if subsession.round_number == 1:
        investments = [0 for i in range(0,16)]
        k=0
        for p in players:
            investments[k] = p.invest
            k=k+1
        investments.sort(reverse=True)
        print(investments)

        #resolving ties:
        if investments[4] == investments[3]:
            investments[4] = investments[4] - 1
        if investments[8] == investments[7]:
            investments[8] = investments[8] - 1
        if investments[12] == investments[11]:
            investments[12] = investments[12] - 1

        matrix = subsession.get_group_matrix()
        print(matrix)
        num_of_groups = len(subsession.get_groups())
        new_matrix = [[0 for i in range(0,4)] for j in range(0,num_of_groups)]

        k1=0
        k2=0
        k3=0
        k4=0
        for p in players:
            if (p.invest > investments[4]) and (k1<4):
                new_matrix[0][k1] = p.id_in_subsession
                k1=k1+1
            elif (p.invest > investments[8]) and (k2<4):
                new_matrix[1][k2] = p.id_in_subsession
                k2=k2+1
            elif (p.invest > investments[12]) and (k3<4):
                new_matrix[2][k3] = p.id_in_subsession
                k3=k3+1
            else:
                new_matrix[3][k4] = p.id_in_subsession
                k4=k4+1
        subsession.set_group_matrix(new_matrix)

    else:
        s_old = subsession.in_round(subsession.round_number - 1)
        old_matrix = s_old.get_group_matrix()
        subsession.set_group_matrix(old_matrix)
#------------------------------------------------------------------


class Group(BaseGroup):
    invest1 = models.IntegerField(initial=0)
    invest2 = models.IntegerField(initial=0)
    invest3 = models.IntegerField(initial=0)
    invest4 = models.IntegerField(initial=0)

    user_name1 = models.StringField()
    user_name2 = models.StringField()
    user_name3 = models.StringField()
    user_name4 = models.StringField()

    rank_1 = models.IntegerField(initial=0)
    rank_2 = models.IntegerField(initial=0)
    rank_3 = models.IntegerField(initial=0)
    rank_4 = models.IntegerField(initial=0)



class Player(BasePlayer):
    user_name = models.StringField(initial = 'default')

    # only suported 1 iteration for now
    iteration = models.IntegerField(initial=0)

    # number of correctly solved real effort tasks:
    num_correct = models.IntegerField(initial=0)
    elapsed_time = models.FloatField(initial=0)

    # amount of money invested in the tournament
    invest = models.IntegerField(initial=0)
    
    # ranking in group
    rank = models.IntegerField(initial=0,min=0,max=4)

    # WTA to sell the certificate:
    WTA = models.FloatField(default=0,max_digits=5, decimal_places=2)
    price_certificate = models.FloatField(default=0,max_digits=5, decimal_places=2)


# puzzle-specific stuff


class Puzzle(ExtraModel):
    """A model to keep record of sliders setup"""

    player = models.Link(Player)
    iteration = models.IntegerField()
    timestamp = models.FloatField()

    num_sliders = models.IntegerField()
    layout = models.LongStringField()

    response_timestamp = models.FloatField()
    num_correct = models.IntegerField(initial=0)
    is_solved = models.BooleanField(initial=False)


class Slider(ExtraModel):
    """A model to keep record of each slider"""

    puzzle = models.Link(Puzzle)
    idx = models.IntegerField()
    target = models.IntegerField()
    value = models.IntegerField()
    is_correct = models.BooleanField(initial=False)
    attempts = models.IntegerField(initial=0)




#-----------------------------------------------------------------------
# SLIDER FUNCS:
def generate_puzzle(player: Player) -> Puzzle:
    """Create new puzzle for a player"""
    params = player.session.params
    num = params['num_sliders']
    layout = task_sliders.generate_layout(params)
    puzzle = Puzzle.create(
        player=player, iteration=player.iteration, timestamp=time.time(),
        num_sliders=num,
        layout=json.dumps(layout)
    )
    for i in range(num):
        target, initial = task_sliders.generate_slider()
        Slider.create(
            puzzle=puzzle,
            idx=i,
            target=target,
            value=initial
        )
    return puzzle


def get_current_puzzle(player):
    puzzles = Puzzle.filter(player=player, iteration=player.iteration)
    if puzzles:
        [puzzle] = puzzles
        return puzzle


def get_slider(puzzle, idx):
    sliders = Slider.filter(puzzle=puzzle, idx=idx)
    if sliders:
        [puzzle] = sliders
        return puzzle


def encode_puzzle(puzzle: Puzzle):
    """Create data describing puzzle to send to client"""
    layout = json.loads(puzzle.layout)
    sliders = Slider.filter(puzzle=puzzle)
    # generate image for the puzzle
    image = task_sliders.render_image(layout, targets=[s.target for s in sliders])
    return dict(
        image=encode_image(image),
        size=layout['size'],
        grid=layout['grid'],
        sliders={s.idx: {'value': s.value, 'is_correct': s.is_correct} for s in sliders}
    )


def get_progress(player: Player):
    """Return current player progress"""
    return dict(
        iteration=player.iteration,
        solved=player.num_correct
    )


def handle_response(puzzle, slider, value):
    slider.value = task_sliders.snap_value(value, slider.target)
    slider.is_correct = slider.value == slider.target
    puzzle.num_correct = len(Slider.filter(puzzle=puzzle, is_correct=True))
    puzzle.is_solved = puzzle.num_correct == puzzle.num_sliders


def play_game(player: Player, message: dict):
    """Main game workflow
    Implemented as reactive scheme: receive message from browser, react, respond.

    Generic game workflow, from server point of view:
    - receive: {'type': 'load'} -- empty message means page loaded
    - check if it's game start or page refresh midgame
    - respond: {'type': 'status', 'progress': ...}
    - respond: {'type': 'status', 'progress': ..., 'puzzle': data}
      in case of midgame page reload

    - receive: {'type': 'new'} -- request for a new puzzle
    - generate new sliders
    - respond: {'type': 'puzzle', 'puzzle': data}

    - receive: {'type': 'value', 'slider': ..., 'value': ...} -- submitted value of a slider
      - slider: the index of the slider
      - value: the value of slider in pixels
    - check if the answer is correct
    - respond: {'type': 'feedback', 'slider': ..., 'value': ..., 'is_correct': ..., 'is_completed': ...}
      - slider: the index of slider submitted
      - value: the value aligned to slider steps
      - is_corect: if submitted value is correct
      - is_completed: if all sliders are correct
    """
    session = player.session
    my_id = player.id_in_group
    params = session.params

    now = time.time()
    # the current puzzle or none
    puzzle = get_current_puzzle(player)

    message_type = message['type']

    if message_type == 'load':
        p = get_progress(player)
        if puzzle:
            return {my_id: dict(type='status', progress=p, puzzle=encode_puzzle(puzzle))}
        else:
            return {my_id: dict(type='status', progress=p)}

    if message_type == "new":
        if puzzle is not None:
            raise RuntimeError("trying to create 2nd puzzle")

        player.iteration += 1
        z = generate_puzzle(player)
        p = get_progress(player)

        return {my_id: dict(type='puzzle', puzzle=encode_puzzle(z), progress=p)}

    if message_type == "value":
        if puzzle is None:
            raise RuntimeError("missing puzzle")
        if puzzle.response_timestamp and now < puzzle.response_timestamp + params["retry_delay"]:
            raise RuntimeError("retrying too fast")

        slider = get_slider(puzzle, int(message["slider"]))

        if slider is None:
            raise RuntimeError("missing slider")
        if slider.attempts >= params['attempts_per_slider']:
            raise RuntimeError("too many slider motions")

        value = int(message["value"])
        handle_response(puzzle, slider, value)
        puzzle.response_timestamp = now
        slider.attempts += 1
        player.num_correct = puzzle.num_correct

        p = get_progress(player)
        return {
            my_id: dict(
                type='feedback',
                slider=slider.idx,
                value=slider.value,
                is_correct=slider.is_correct,
                is_completed=puzzle.is_solved,
                progress=p,
            )
        }

    if message_type == "cheat" and settings.DEBUG:
        return {my_id: dict(type='solution', solution={s.idx: s.target for s in Slider.filter(puzzle=puzzle)})}

    raise RuntimeError("unrecognized message from client")
#-----------------------------------------------------------------------







#-----------------------------------------------------------------------
# CC FUNCTIONS:


# setting the ranking:
def set_ranking(group: Group):
    players  = group.get_players()

    investments = [0 for x in range(0,4)]
    usernames = [0 for x in range(0,4)]
    ranks = [0 for x in range(0,4)]

    investments = [0 for x in range(0,4)]
    usernames = {}
    i=0
    for p in players:
        investments[i] = p.invest
        i=i+1

    investments = sorted(investments,reverse = True)

    k=0
    u = 0
    group.invest1 = investments[k]
    for p in players:
        if p.invest == investments[k] and p.rank==0:
            p.rank = k+1
            usernames[u] = p.user_name
            u=u+1

    k=1
    group.invest2 = investments[k]
    for p in players:
        if p.invest == investments[k] and p.rank==0:
            p.rank = k+1
            usernames[u] = p.user_name
            u=u+1

    k=2
    group.invest3 = investments[k]
    for p in players:
        if p.invest == investments[k] and p.rank==0 :
            p.rank = k+1
            usernames[u] = p.user_name
            u=u+1

    k=3
    group.invest4 = investments[k]
    for p in players:
        if p.invest == investments[k] and p.rank==0:
            p.rank = k+1
            usernames[u] = p.user_name
            u=u+1
    ranks = [0 for i in range(0,4)]
    i=0
    for p in players: 
        ranks[i] = p.rank
        i=i+1
    ranks = sorted(ranks,reverse = False)


    group.user_name1 = usernames[0]
    group.user_name2 = usernames[1]
    group.user_name3 = usernames[2]
    group.user_name4 = usernames[3]

    group.rank_1 = ranks[0]
    group.rank_2 = ranks[1]
    group.rank_3 = ranks[2]
    group.rank_4 = ranks[3]

    group.invest1 = investments[0]
    group.invest2 = investments[1]
    group.invest3 = investments[2]
    group.invest4 = investments[3]





#-----------------------------------------------------------------------




class RealEffortTask(Page):
    template_name = '_static/global/Sliders.html'

    timeout_seconds = Constants.task_time

    live_method = play_game

    @staticmethod
    def js_vars(player: Player):
        return dict(
            params=player.session.params,
            slider_size=task_sliders.SLIDER_BBOX,
        )

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            params=player.session.params,
            DEBUG=settings.DEBUG,
            round_number = player.round_number,
            num_rounds = Constants.num_rounds
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.subsession.round_number==1:
            set_paying_round(player.subsession)

        puzzle = get_current_puzzle(player)

        if puzzle and puzzle.response_timestamp:
            player.elapsed_time = puzzle.response_timestamp - puzzle.timestamp
            player.num_correct = puzzle.num_correct
#            player.payoff = player.num_correct

class Welcome(Page):
    def is_displayed(player):
        return player.round_number == 1

class Instructions(Page):
    def is_displayed(player):
        return player.round_number == 1


class GenerateUsername(Page):
    def is_displayed(player):
        if player.round_number > 1:
            p = player.in_round(player.round_number-1)
            player.user_name = p.user_name

        return player.round_number == 1

    def live_method(player, data):
        temp = generate_username(1)
        player.user_name = temp[0]
        for p in player.in_all_rounds():
            p.user_name = temp[0]
#        print(temp[0])
        return {player.id_in_group : temp}

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        temp = player.user_name
        for p in player.in_all_rounds():
          p.user_name  = temp



class Invest(Page):
    form_model='player'
    form_fields = ['invest']

    def vars_for_template(player: Player):
        return dict(
            user_name = player.user_name,
            earnings = player.num_correct,
            round_number = player.round_number,
            num_rounds = Constants.num_rounds
            )

class InvestWaitPage(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def after_all_players_arrive(subsession: Subsession):    
        set_groups(subsession)
        for g in subsession.get_groups():
            set_ranking(g)

class TournamentResults(Page):
#    template_name = '_static/global/TournamentResults.html'

    def vars_for_template(player: Player):
        temp = [player.group.invest1, player.group.invest2, player.group.invest3, player.group.invest4]
        user_names = [player.group.user_name1, player.group.user_name2, player.group.user_name3, player.group.user_name4]
        ranks = [player.group.rank_1, player.group.rank_2, player.group.rank_3, player.group.rank_4]
        tournament = [0 for x in range(0,4)]
        for i in range(0,4):
            tournament[i] = [ranks[i], temp[i], user_names[i]]
        payment = player.num_correct - player.invest

        return dict(
            user_name = player.user_name,
            earnings = player.num_correct,
            invest = player.invest,
            rank = player.rank,
            pay = payment,
            tournament = tournament,
            round_number = player.round_number,
            num_rounds = Constants.num_rounds
            )
        
    def before_next_page(player:Player, timeout_happened):
        if player.subsession.round_number == Constants.num_rounds:
            p = player.in_round(player.subsession.paying_round)
            player.participant.vars['T1_earnings'] = p.num_correct
            player.participant.vars['user_name'] = p.user_name



page_sequence = [
#            Welcome,
            Instructions,
            GenerateUsername,
            RealEffortTask,
            Invest,
            InvestWaitPage,
            TournamentResults,
            ]


