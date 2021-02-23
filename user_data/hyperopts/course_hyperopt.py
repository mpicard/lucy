# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# isort: skip_file

from functools import reduce
from typing import Any, Callable, Dict, List

import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame
from skopt.space import Categorical, Dimension, Integer, Real  # noqa

from freqtrade.optimize.hyperopt_interface import IHyperOpt

import talib.abstract as ta  # noqa
import freqtrade.vendor.qtpylib.indicators as qtpylib


class CourseHyperOpt(IHyperOpt):
    """
    CourseHyperOpt for CourseStrategy
    """

    @staticmethod
    def populate_indicators(dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["rsi"] = ta.RSI(dataframe)

        bollinger = qtpylib.bollinger_bands(
            qtpylib.typical_price(dataframe), window=20, stds=1
        )
        dataframe["bb1_lowerband"] = bollinger["lower"]
        dataframe["bb1_middleband"] = bollinger["mid"]
        dataframe["bb1_upperband"] = bollinger["upper"]

        bollinger = qtpylib.bollinger_bands(
            qtpylib.typical_price(dataframe), window=20, stds=2
        )
        dataframe["bb2_lowerband"] = bollinger["lower"]
        dataframe["bb2_middleband"] = bollinger["mid"]
        dataframe["bb2_upperband"] = bollinger["upper"]

        bollinger = qtpylib.bollinger_bands(
            qtpylib.typical_price(dataframe), window=20, stds=3
        )
        dataframe["bb3_lowerband"] = bollinger["lower"]
        dataframe["bb3_middleband"] = bollinger["mid"]
        dataframe["bb3_upperband"] = bollinger["upper"]

        bollinger = qtpylib.bollinger_bands(
            qtpylib.typical_price(dataframe), window=20, stds=4
        )
        dataframe["bb4_lowerband"] = bollinger["lower"]
        dataframe["bb4_middleband"] = bollinger["mid"]
        dataframe["bb4_upperband"] = bollinger["upper"]

        return dataframe

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
            if "rsi-enabled" in params and params["rsi-enabled"]:
                conditions.append(dataframe["rsi"] > params["rsi-value"])

            # TRIGGERS
            if "trigger" in params:
                if params["trigger"] == "bb1_lower":
                    conditions.append(dataframe["close"] < dataframe["bb1_lowerband"])
                if params["trigger"] == "bb2_lower":
                    conditions.append(dataframe["close"] < dataframe["bb2_lowerband"])
                if params["trigger"] == "bb3_lower":
                    conditions.append(dataframe["close"] < dataframe["bb3_lowerband"])
                if params["trigger"] == "bb4_lower":
                    conditions.append(dataframe["close"] < dataframe["bb4_lowerband"])

            # Check that volume is not 0
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
            Integer(5, 50, name="rsi-value"),
            Categorical([True, False], name="rsi-enabled"),
            Categorical(
                [
                    "bb1_lower",
                    "bb2_lower",
                    "bb3_lower",
                    "bb4_lower",
                ],
                name="trigger",
            ),
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
            if "sell-rsi-enabled" in params and params["sell-rsi-enabled"]:
                conditions.append(dataframe["rsi"] > params["sell-rsi-value"])

            # TRIGGERS
            if "sell-trigger" in params:
                if params["sell-trigger"] == "sell-bb1_lower":
                    conditions.append(dataframe["close"] > dataframe["bb1_lowerband"])
                if params["sell-trigger"] == "sell-bb1_middle":
                    conditions.append(dataframe["close"] > dataframe["bb1_middleband"])
                if params["sell-trigger"] == "sell-bb1_upper":
                    conditions.append(dataframe["close"] > dataframe["bb1_upperband"])

            # Check that volume is not 0
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
            Integer(30, 100, name="sell-rsi-value"),
            Categorical([True, False], name="sell-rsi-enabled"),
            Categorical(
                ["sell-bb1_lower", "sell-bb1_middle", "sell-bb1_upper"],
                name="sell-trigger",
            ),
        ]
