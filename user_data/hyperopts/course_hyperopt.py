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
                conditions.append(dataframe["rsi"] < params["rsi-value"])

            # TRIGGERS
            if "trigger" in params:
                if params["trigger"] == "bb_lower":
                    conditions.append(dataframe["close"] < dataframe["bb_lowerband"])

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
            Integer(20, 40, name="rsi-value"),
            Categorical([True, False], name="rsi-enabled"),
            Categorical(["bb_lower"], name="trigger"),
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
                if params["sell-trigger"] == "sell-bb_upper":
                    conditions.append(dataframe["close"] > dataframe["bb_upperband"])

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
            Integer(60, 100, name="sell-rsi-value"),
            Categorical([True, False], name="sell-rsi-enabled"),
            Categorical(["sell-bb_upper"], name="sell-trigger"),
        ]

    @staticmethod
    def generate_roi_table(params: Dict) -> Dict[int, float]:
        """
        Generate the ROI table that will be used by Hyperopt
        """
        roi_table = {}
        roi_table[0] = params["roi_p1"] + params["roi_p2"] + params["roi_p3"]
        roi_table[params["roi_t3"]] = params["roi_p1"] + params["roi_p2"]
        roi_table[params["roi_t3"] + params["roi_t2"]] = params["roi_p1"]
        roi_table[params["roi_t3"] + params["roi_t2"] + params["roi_t1"]] = 0

        return roi_table

    @staticmethod
    def roi_space() -> List[Dimension]:
        """
        Values to search for each ROI step
        """
        return [
            Integer(10, 120, name="roi_t1"),
            Integer(10, 60, name="roi_t2"),
            Integer(10, 40, name="roi_t3"),
            Real(0.01, 0.04, name="roi_p1"),
            Real(0.01, 0.07, name="roi_p2"),
            Real(0.01, 0.20, name="roi_p3"),
        ]

    @staticmethod
    def stoploss_space() -> List[Dimension]:
        """
        Stoploss value to search for
        """
        return [Real(-0.5, -0.02, name="stoploss")]

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators. Should be a copy of same method from strategy.
        Must align to populate_indicators in this file.
        Only used when --spaces does not include buy space.
        """
        dataframe.loc[
            (
                (dataframe["close"] < dataframe["bb_lowerband"])
                & (dataframe["rsi"] < 21)
            ),
            "buy",
        ] = 1

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators. Should be a copy of same method from strategy.
        Must align to populate_indicators in this file.
        Only used when --spaces does not include sell space.
        """
        dataframe.loc[
            (
                (qtpylib.crossed_above(dataframe["macdsignal"], dataframe["macd"]))
                & (dataframe["fastd"] > 54)
            ),
            "sell",
        ] = 1

        return dataframe
