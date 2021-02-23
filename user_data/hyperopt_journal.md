2021-02-23 18:08:13,297 - freqtrade.optimize.hyperopt - INFO - 250 epochs saved to '/freqtrade/user_data/hyperopt_results/hyperopt_results_2021-02-23_17-56-13.pickle'.

Best result:

193/250: 609 trades. 259/233/117 Wins/Draws/Losses. Avg profit 0.30%. Median profit 0.00%. Total profit 0.01841615 BTC ( 183.98Σ%). Avg duration 5002.1 min. Objective: -0.95059

    # Buy hyperspace params:
    buy_params = {
     'rsi-enabled': True, 'rsi-value': 18, 'trigger': 'bb4_lower'
    }

    # Sell hyperspace params:
    sell_params = {
        'sell-rsi-enabled': True,
        'sell-rsi-value': 72,
        'sell-trigger': 'sell-bb1_lower'
    }

    # ROI table:
    minimal_roi = {
        "0": 0.27614,
        "298": 0.20814,
        "972": 0.09077,
        "2297": 0
    }

    # Stoploss:
    stoploss = -0.31226
