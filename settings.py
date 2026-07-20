from os import environ

SESSION_CONFIGS = [
    #     dict(
    #        name="AA_control",
    #        display_name="Competition Control Treatment",
    #        num_demo_participants=4,
    #        app_sequence=["AA_control"],
    #    ),
    #     dict(
    #         name ='ArbitrationDS',
    #         display_name ='Arbitration Dominant Strategies (DS)',
    #         num_demo_participants = 2,
    #         app_sequence = ['Consent_GER','WelcomeScreen', 'Arbitration_DS','beauty_contest','risk_elicitation','FinalResults'],
    #     ),
    #     dict(
    #         name ='ArbitrationSS',
    #         display_name ='Arbitration Strategically Simple (SS)',
    #         num_demo_participants = 2,
    #         app_sequence = ['Consent_GER','WelcomeScreen','Arbitration_SS','beauty_contest','risk_elicitation','FinalResults'],
    #     ),
    #     dict(
    #         name ='ArbitrationSRD1',
    #         display_name ='Arbitration Srictly Range Dominant: Uninanimuous Agreement (SRD1)',
    #         num_demo_participants = 2,
    #         app_sequence = ['Consent_GER','WelcomeScreen','Arbitration_SRD1','beauty_contest','risk_elicitation','FinalResults'],
    #     ),
    #     dict(
    #         name ='ArbitrationSRD2',
    #         display_name ='Arbitration Srictly Range Dominant: Veto (SRD2)',
    #         num_demo_participants = 2,
    #         app_sequence = ['Consent_GER','WelcomeScreen','Arbitration_SRD2','beauty_contest','risk_elicitation','FinalResults'],
    #     ),
    #     dict(
    #         name ='ArbitrationSRD2_voting',
    #         display_name ='Arbitration Srictly Range Dominant: Veto (SRD2), with two votes',
    #         num_demo_participants = 2,
    #         app_sequence = ['Consent_GER','WelcomeScreen','Arbitration_SRD2_voting','beauty_contest','risk_elicitation','FinalResults'],
    #     ),
    #     dict(
    #         name ='Simple_NormalForm_DS',
    #         display_name ='Simplicity in Games: Normal Forms x DS',
    #         num_demo_participants = 2,
    #         app_sequence = ['Simple_NormalForm_DS'],
    #     ),
    #     dict(
    #         name ='Simple_NF_RD1',
    #         display_name ='Simplicity in Games: Normal Forms x RD1',
    #         num_demo_participants = 2,
    #         app_sequence = ['Simple_NF_RD1'],
    #     ),
    #     dict(
    #         name ='Simple_NF_RD2',
    #         display_name ='Simplicity in Games: Normal Forms x RD2',
    #         num_demo_participants = 2,
    #         app_sequence = ['Simple_NF_RD2'],
    #     ),
    #     dict(
    #         name ='Simple_NF_SS',
    #         display_name ='Simplicity in Games: Normal Forms x SS',
    #         num_demo_participants = 2,
    #         app_sequence = ['Simple_NF_SS'],
    #     ),
    #     dict(
    #         name ='Beauty_Contest',
    #         display_name ='Beauty Contest',
    #         num_demo_participants = 2,
    #         app_sequence = ['beauty_contest'],
    #     ),
    #     dict(
    #         name ='RiskElicitation',
    #         display_name ='Risk Elicitation',
    #         num_demo_participants = 1,
    #         app_sequence = ['risk_elicitation'],
    #     ),
    #     dict(
    #         name ='FinalResults',
    #         display_name ='Survey',
    #         num_demo_participants = 1,
    #         app_sequence = ['FinalResults'],
    #     ),
    #     dict(
    #         name ='WelcomeScreen',
    #         display_name ='Welcome Screen',
    #         num_demo_participants = 1,
    #         app_sequence = ['WelcomeScreen'],
    #     ),
    #    dict(
    #        name="CC_T0",
    #        display_name="Consp Consumption: Cardinal Visibility",
    #        num_demo_participants=4,
    #        app_sequence=["CC_T0","CC_FinalResults"],
    #    ),
    #    dict(
    #        name="CC_CV_BR",
    #        display_name="Consp Consumption: Cardinal Visibility and Best Response",
    #        num_demo_participants=4,
    #        app_sequence=["CC_CV_BR","CC_FinalResults"],
    #    ),
    #    dict(
    #        name="CC_CV_PAM",
    #        display_name="Consp Consumption: Cardinal Visibility, Positive Assortative Matching",
    #        num_demo_participants=4,
    #        app_sequence=["CC_CardinalVis_PAM","CC_FinalResults"],
    #    ),
    #    dict(
    #        name="CC_CV_NAM",
    #        display_name="Consp Consumption: Cardinal Visibility, Negative Assortative Matching",
    #        num_demo_participants=4,
    #        app_sequence=["CC_CV_NAM","CC_FinalResults"],
    #    ),
    #    dict(
    #        name="CC_OrdinalVisibility",
    #        display_name="Consp Consumption: Ordinal Visibility",
    #        num_demo_participants=4,
    #        app_sequence=["CC_OrdinalVisibility","CC_FinalResults"],
    #    ),
    #     dict(
    #        name="CC_NoVisibility",
    #        display_name="Consp Consumption: No Visibility",
    #        num_demo_participants=4,
    #        app_sequence=["CC_NoVisibility","CC_FinalResults"],
    #    ),
    #    dict(
    #        name="CC_NV_BR",
    #        display_name="Consp Consumption: No Visibility and Best Response",
    #        num_demo_participants=4,
    #        app_sequence=["CC_NV_BR","CC_FinalResults"],
    #    ),
    #    dict(
    #        name="CC_NV_PAM",
    #        display_name="Consp Consumption: No Visibility, Positive Assortative Matching",
    #        num_demo_participants=4,
    #        app_sequence=["CC_NV_PAM","CC_FinalResults"],
    #    ),
    #    dict(
    #        name="CC_NV_NAM",
    #        display_name="Consp Consumption: No Visibility, Negative Assortative Matching",
    #        num_demo_participants=4,
    #        app_sequence=["CC_NV_NAM","CC_FinalResults"],
    #    ),
    #    dict(
    #        name="CC_BestResponse",
    #        display_name="Consp Consumption: Best Response",
    #        num_demo_participants=1,
    #        app_sequence=["CC_BestResponse"],
    #    ),
    #    dict(
    #         name='Attention_Welfare_Experiment',
    #         display_name='Attention Welfare Experiment',
    #         app_sequence=['attention_welfare_choice'],
    #         num_demo_participants=1,
    #     ),
    #    dict(
    #        name='procedures_T0',
    #        display_name='Choices and Procedures, T0: Delegated Procedure. Prearranged sequence of all binary comparisons, at each stage subject discards one of the alternatives.',
    #        app_sequence=['Procedures_Consent_form','procedures_T0','finish_Prolific'],
    #        num_demo_participants=1,
    #        ),
    #    dict(
    #        name='procedures_T1',
    #        display_name='Choices and Procedures, T1: Assisted Binary  Procedure. Free Choise of Binary Comparisons, with no more than two cards open at the same time and no returning discarded alternatives.',
    #        app_sequence=['Procedures_Consent_form','procedures_T1','finish_Prolific'],
    #        num_demo_participants=1,
    #        ),
    #    dict(
    #        name='procedures_T2a',
    #        display_name='Choices and Procedures, T2a: Assisted  Procedure A. Free choice to open several cards (no limit on how many), no returning of the discarded cards.',
    #        app_sequence=['Procedures_Consent_form','procedures_T2a','finish_Prolific'],
    #        num_demo_participants=1,
    #        ),
    #    dict(
    #        name='procedures_T2b',
    #        display_name='Choices and Procedures, T2b: Assisted  Procedure B. Free choice to open several cards (no limits on how many) with possibility to return the discarded cards.',
    #        app_sequence=['Procedures_Consent_form','procedures_T2b','finish_Prolific'],
    #        num_demo_participants=1,
    #        ),
    #    dict(
    #        name='procedures_T3',
    #        display_name='Choices and Procedures, T3: Free  Procedure. All cards are open, choosing the element without procedure tracking. ',
    #        app_sequence=['Procedures_Consent_form','procedures_T3','finish_Prolific'],
    #        num_demo_participants=1,
    #        ),
    #    dict(
    #        name="Dynamic_Contracts_Consent",
    #        display_name="Dynamic_Contracts_Consent_Form",
    #        num_demo_participants=1,
    #        treatment = 0,
    #        app_sequence=["SBC_consent_form"],
    #    ),
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
    completion_url="https://app.prolific.com/submissions/complete?cc=C13H5EHD",
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
