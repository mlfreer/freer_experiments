from os import environ

SESSION_CONFIGS = [
    dict(
        name="Dynamic_Contracts_S1_t1",
        display_name="Dynamic_Contracts t=1 (Static, Upfront Payment)",
        num_demo_participants=1,
        treatment=0,
        app_sequence=["SBC_consent_form", "SBC_S1_t1_"],
    ),
    dict(
        name="Dynamic_Contracts_S2_t1",
        display_name="Dynamic_Contracts t=1 (Static, t=2 Payment)",
        num_demo_participants=1,
        treatment=1,
        app_sequence=["SBC_consent_form", "SBC_S1_t1_"],
    ),  # ?participant_label?participant_label=00001
    dict(
        name="Dynamic_Contracts_D1_t1",
        display_name="Dynamic_Contracts t=1 (Dynamic, Option to buy)",
        num_demo_participants=1,
        treatment=2,
        app_sequence=["SBC_consent_form", "SBC_S1_t1_"],
    ),
    dict(
        name="Dynamic_Contracts_D2_t1",
        display_name="Dynamic_Contracts t=1 (Dynamic, Refund)",
        num_demo_participants=1,
        treatment=3,
        app_sequence=["SBC_consent_form", "SBC_S1_t1_"],
    ),
    dict(
        name="Dynamic_Contracts_S1_t2",
        display_name="Period: t=2, for all treatments",
        num_demo_participants=1,
        treatment=0,
        app_sequence=["SBC_consent_t2", "SBC_S1_t2_"],
    ),
]

# ------------------------------------------------------------------------------------
# SWITCHING THE DEBUG MODE ON AND OFF
DEBUG = True
# ------------------------------------------------------------------------------------


# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00,
    participation_fee=2.00,
    min_pay=1,
    max_pay=28,
    A_BAR=8,
    treatment=0,  # treatment enumeration starts with 0 and goes to 3 so we can simplify the presentation of the constants.
    doc="",
    completion_url="https://app.prolific.com/submissions/complete?cc=CDT8MBD8",
    completion_url1="https://app.prolific.com/submissions/complete?cc=C13H5EHD",
    selected_for_payment=10,  # the probability that subject is selected for payment
    overwrite_decision=2,  # decision in t=1 is over-written
)

ROOMS = [
    dict(
        name="econ_lab",
        display_name="Economics Lab",
        participant_label_file="econ_lab.txt",
        #        use_secure_urls=False
    ),
    {
        "name": "live_demo",
        "display_name": "Room for live demo (no participant labels)",
    },
    dict(
        name="Prolific_Study_S1",
        display_name="Prolific_Study_S1",
        # participant_label_file='_rooms/your_study.txt',
        # use_secure_urls=True,
    ),
    # https://freer-experiments.herokuapp.com/room/Prolific_Study_A?participant_label={{%PROLIFIC_PID%}}&STUDY_ID={{%STUDY_ID%}}&SESSION_ID={{%SESSION_ID%}}
    dict(
        name="Prolific_Study_S2",
        display_name="Prolific_Study_S2",
        # participant_label_file='_rooms/your_study.txt',
        # use_secure_urls=True,
    ),
    dict(
        name="Prolific_Study_D1",
        display_name="Prolific_Study_D1",
        # participant_label_file='_rooms/your_study.txt',
        # use_secure_urls=True,
    ),
    dict(
        name="Prolific_Study_D2",
        display_name="Prolific_Study_D2",
        # participant_label_file='_rooms/your_study.txt',
        # use_secure_urls=True,
    ),
    dict(
        name="Prolific_Study_T2",
        display_name="Prolific_Study_T2",
        # participant_label_file='_rooms/your_study.txt',
        # use_secure_urls=True,
    ),
]

PARTICIPANT_FIELDS = [
    "price_order_t1",
    "price_order_t2",
    "random_draw_1",
    "random_draw_2",
    "selected_round",
    "params",
    "x_draw",
    "treatment",
    "indexes",
    "rounds",  # to record per round outcomes
]
SESSION_FIELDS = []
participation_fee = 2

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = "en"

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = "GBP"
REAL_WORLD_CURRENCY_DECIMAL_PLACES = 0
USE_POINTS = False

ADMIN_USERNAME = "admin"
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get("OTREE_ADMIN_PASSWORD")

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = "4284616162474"
