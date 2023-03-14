from os import environ

SESSION_CONFIGS = [
     dict(
         name='Attention_Welfare_Experiment',
         display_name='Attention Welfare Experiment',
         app_sequence=['attention_welfare_choice'],
         num_demo_participants=1,
     ),
     dict(
         name = 'simple_voting_3P_DS_GC_indirect',
         display_name='Simple Voting: 3P x Dominat Strategy x Dynamic x Good Compromise',
         app_sequence=['simple_voting_3P_DS_GC_indirect'],
         num_demo_participants=3,
     ),
     dict(
         name = 'simple_voting_3P_FB_GC_indirect',
         display_name='Simple Voting: 3P x First Order Beliefs x Dynamic x Good Compromise',
         app_sequence=['simple_voting_3P_FB_GC_indirect'],
         num_demo_participants=3,
     ),
     dict(
         name = 'simple_voting_3P_MAJ_GC_indirect',
         display_name='Simple Voting: 3P x Majority x Dynamic x Good Compromise',
         app_sequence=['simple_voting_3P_MAJ_GC_indirect'],
         num_demo_participants=3,
     ),
     dict(
         name ='Beauty_Contest',
         display_name ='Beauty Contest',
         num_demo_participants = 2,
         app_sequence = ['beauty_contest'],
     ),
     dict(
         name ='RiskElicitation',
         display_name ='Risk Elicitation',
         num_demo_participants = 1,
         app_sequence = ['risk_elicitation'],
     ),
]

#------------------------------------------------------------------------------------
# SWITCHING THE DEBUG MODE ON AND OFF
DEBUG = True
#------------------------------------------------------------------------------------





# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

ROOMS = [
    dict(
        name='econ_lab',
        display_name='Economics Lab',
        participant_label_file='econ_lab.txt',
#        use_secure_urls=False
    ),
]

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'GBP'
USE_POINTS = False

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '4284616162474'
