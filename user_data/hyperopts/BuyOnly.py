# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement

# --- Do not remove these libs ---
from functools import reduce
from typing import Any, Callable, Dict, List

import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame
from skopt.space import Categorical, Dimension, Integer, Real  # noqa

from freqtrade.optimize.hyperopt_interface import IHyperOpt

# --------------------------------
# Add your lib to import here
import talib.abstract as ta  # noqa
import freqtrade.vendor.qtpylib.indicators as qtpylib


class BuyOnly(IHyperOpt):
    """
    This is a Hyperopt template to get you started.

    More information in the documentation: https://www.freqtrade.io/en/latest/hyperopt/

    You should:
    - Add any lib you need to build your hyperopt.

    You must keep:
    - The prototypes for the methods: populate_indicators, indicator_space, buy_strategy_generator.

    The methods roi_space, generate_roi_table and stoploss_space are not required
    and are provided by default.
    However, you may override them if you need 'roi' and 'stoploss' spaces that
    differ from the defaults offered by Freqtrade.
    Sample implementation of these methods will be copied to `user_data/hyperopts` when
    creating the user-data directory using `freqtrade create-userdir --userdir user_data`,
    or is available online under the following URL:
    https://github.com/freqtrade/freqtrade/blob/develop/freqtrade/templates/sample_hyperopt_advanced.py.
    """

    @staticmethod
    def buy_strategy_generator(params: Dict[str, Any]) -> Callable:
        def populate_buy_trend(dataframe: DataFrame, metadata: dict) -> DataFrame:
            conditions = []

            # GUARDS AND TRENDS
            if params.get("tema-enabled"):
                conditions.append(dataframe["tema"] > dataframe["tema"].shift(1))
            if params.get("bb-lowerband-enabled"):
                conditions.append(dataframe["open"] <= dataframe["bb_lowerband"])

            # TRIGGERS
            if "trigger" in params:
                if params["trigger"] == "rsi_cross_signal":
                    conditions.append(
                        qtpylib.crossed_above(dataframe["rsi"], params["rsi-value"])
                    )

            conditions.append(dataframe["volume"] > 0)

            if conditions:
                dataframe.loc[reduce(lambda x, y: x & y, conditions), "buy"] = 1
            return dataframe

        return populate_buy_trend

    @staticmethod
    def indicator_space() -> List[Dimension]:
        return [
            Categorical([True, False], name="tema-enabled"),
            Categorical([True, False], name="bb-lowerband-enabled"),
            Integer(5, 50, name="rsi-value"),
            Categorical(["rsi_cross_signal"], name="trigger"),
        ]

    @staticmethod
    def sell_strategy_generator(params: Dict[str, Any]) -> Callable:
        def populate_sell_trend(dataframe: DataFrame, metadata: dict) -> DataFrame:
            return dataframe

        return populate_sell_trend

    @staticmethod
    def sell_indicator_space() -> List[Dimension]:
        return []
