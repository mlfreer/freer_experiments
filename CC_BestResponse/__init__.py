import time
import json

from otree import settings
from otree.api import *
import random

from _static import task_sliders
#from _static import encode_image
from _static.image_utils import encode_image

doc = """
"""


class Constants(BaseConstants):
    name_in_url = "CC_BestResponse"
    players_per_group = None
    num_rounds = 1

    task_time = 60

    tournament = [25, 20, 10]



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

def set_paying_round(session: Subsession):
    p_round = random.randint(1,Constants.num_rounds)
    s = session.in_round(Constants.num_rounds)
    s.paying_round = p_round
#------------------------------------------------------------------



class Group(BaseGroup):
    pass

class Player(BasePlayer):
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

    # investments:
    invest1 = models.IntegerField(initial=0)
    invest2 = models.IntegerField(initial=0)
    invest3 = models.IntegerField(initial=0)
    invest4 = models.IntegerField(initial=0)


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
def set_ranking(player: Player):
    investments = Constants.tournament

    k=0
    if player.invest >= investments[k] and player.rank==0:
        player.rank = k+1

    k=1
    if player.invest >= investments[k] and player.rank==0:
        player.rank = k+1

    k=2
    if player.invest >= investments[k] and player.rank==0:
        player.rank = k+1

    k=3
    if player.invest < investments[k-1] and player.rank==0:
        player.rank = k+1

    invest = [Constants.tournament[0], Constants.tournament[1], Constants.tournament[2], player.invest]
    invest = sorted(invest,reverse = True)
    player.invest1 = invest[0]
    player.invest2 = invest[1]
    player.invest3 = invest[2]
    player.invest4 = invest[3]





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
            DEBUG=settings.DEBUG
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

class Invest(Page):
    form_model='player'
    form_fields = ['invest']

    def vars_for_template(player: Player):
        tournament = [0 for x in range(0,3)]
        for i in range(0,3):
            tournament[i] = [i+1, Constants.tournament[i]]

        return dict(
            earnings = player.num_correct,
            tournament = tournament
            )
    def before_next_page(player:Player,timeout_happened):
        set_ranking(player)


#class InvestWaitPage(WaitPage):
#    wait_for_all_groups = False
#
#    @staticmethod
#    def after_all_players_arrive(group: Group):
#        set_ranking(group)

class TournamentResults(Page):
    template_name = '_static/global/TournamentResults.html'

    def vars_for_template(player: Player):
        temp = [player.invest1, player.invest2, player.invest3, player.invest4]
        tournament = [0 for x in range(0,4)]
        for i in range(0,4):
            tournament[i] = [i+1, temp[i]]


        return dict(
            earnings = player.num_correct,
            invest = player.invest,
            rank = player.rank,
            tournament = tournament
            )

class WTA(Page):
    template_name = '_static/global/WTA.html'

    form_model='player'
    form_fields = ['WTA']

    def vars_for_template(player: Player):
        temp = [player.invest1, player.invest2, player.invest3, player.invest4]
        tournament = [0 for x in range(0,4)]
        for i in range(0,4):
            tournament[i] = [i+1, temp[i]]


        return dict(
            earnings = player.num_correct,
            invest = player.invest,
            rank = player.rank,
            tournament = tournament
            )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        number = round(10*random.random(),1)
        if number >= player.WTA:
            player.price_certificate = number
        else:
            player.price_certificate=-1


class Results(Page):
    template_name = '_static/global/Results.html'

    def vars_for_template(player: Player):
        temp = [player.invest1, player.invest2, player.invest3, player.invest4]
        tournament = [0 for x in range(0,4)]
        for i in range(0,4):
            tournament[i] = [i+1, temp[i]]

        if player.subsession.round_number == Constants.num_rounds:
            p = player.in_round(player.subsession.paying_round)
            player.participant.vars['T2_earnings'] = p.num_correct
            player.participant.vars['T2_certificate'] = p.price_certificate

        return dict(
            earnings = player.num_correct,
            invest = player.invest,
            rank = player.rank,
            tournament = tournament,
            price_certificate = player.price_certificate
            )


page_sequence = [
            RealEffortTask,
            Invest,
            TournamentResults,
            WTA,
            Results
            ]


