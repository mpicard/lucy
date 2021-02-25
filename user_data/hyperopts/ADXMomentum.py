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


class ADXMomentum(IHyperOpt):
    @staticmethod
    def buy_strategy_generator(params: Dict[str, Any]) -> Callable:
        """
        Define the buy strategy parameters to be used by Hyperopt.
        """

        def populate_buy_trend(dataframe: DataFrame, metadata: dict) -> DataFrame:
            """
            Buy strategy Hyperopt will build and use.
            """
            conditions = []

            # GUARDS AND TRENDS
            conditions.append(dataframe["adx"] > params["adx-value"])
            conditions.append(dataframe["mom"] > params["mom-value"])
            conditions.append(dataframe["plus_di"] > params["plus_di-value"])
            conditions.append(dataframe["plus_di"] > dataframe["minus_di"])

            # Check that the candle had volume
            conditions.append(dataframe["volume"] > 0)

            if conditions:
                dataframe.loc[reduce(lambda x, y: x & y, conditions), "buy"] = 1

            return dataframe

        return populate_buy_trend

    @staticmethod
    def indicator_space() -> List[Dimension]:
        """
        Define your Hyperopt space for searching buy strategy parameters.
        """
        return [
            Integer(20, 50, name="adx-value"),
            Integer(-50, 50, name="mom-value"),
            Integer(0, 50, name="plus_di-value"),
        ]

    @staticmethod
    def sell_strategy_generator(params: Dict[str, Any]) -> Callable:
        """
        Define the sell strategy parameters to be used by Hyperopt.
        """

        def populate_sell_trend(dataframe: DataFrame, metadata: dict) -> DataFrame:
            """
            Sell strategy Hyperopt will build and use.
            """
            conditions = []

            # GUARDS AND TRENDS
            conditions.append(dataframe["adx"] > params["sell-adx-value"])
            conditions.append(dataframe["mom"] > params["sell-mom-value"])
            conditions.append(dataframe["minus_di"] > params["sell-minus_di-value"])
            conditions.append(dataframe["plus_di"] < dataframe["minus_di"])

            # Check that the candle had volume
            conditions.append(dataframe["volume"] > 0)

            if conditions:
                dataframe.loc[reduce(lambda x, y: x & y, conditions), "sell"] = 1

            return dataframe

        return populate_sell_trend

    @staticmethod
    def sell_indicator_space() -> List[Dimension]:
        """
        Define your Hyperopt space for searching sell strategy parameters.
        """
        return [
            Integer(50, 100, name="sell-adx-value"),
            Integer(-50, 50, name="sell-mom-value"),
            Integer(50, 100, name="sell-minus_di-value"),
            Integer(60, 100, name="sell-rsi-value"),
        ]
