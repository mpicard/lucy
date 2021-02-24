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


class CofiBitHyperopt(IHyperOpt):
    @staticmethod
    def buy_strategy_generator(params: Dict[str, Any]) -> Callable:
        def populate_buy_trend(dataframe: DataFrame, metadata: dict) -> DataFrame:
            conditions = []

            # GUARDS AND TRENDS
            if params.get("ema-low-enabled"):
                conditions.append(dataframe["open"] < dataframe["ema-low"])
            if params.get("fastk-enabled"):
                conditions.append(dataframe["fastk"] < params["fastk-value"])
            if params.get("fastd-enabled"):
                conditions.append(dataframe["fastd"] < params["fastd-value"])
            if params.get("adx-enabled"):
                conditions.append(dataframe["adx"] > params["adx-value"])

            # TRIGGERS
            if "trigger" in params:
                if params["trigger"] == "fastk_cross_fastd":
                    conditions.append(
                        qtpylib.crossed_above(dataframe["fastk"], dataframe["fastd"])
                    )

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
            Integer(0, 100, name="fastk-value"),
            Integer(0, 100, name="fastd-value"),
            Integer(5, 80, name="adx-value"),
            Categorical([True, False], name="ema-low-enabled"),
            Categorical([True, False], name="fastk-enabled"),
            Categorical([True, False], name="fastd-enabled"),
            Categorical([True, False], name="adx-enabled"),
            Categorical(["fastk_cross_fastd"], name="trigger"),
        ]

    @staticmethod
    def sell_strategy_generator(params: Dict[str, Any]) -> Callable:
        def populate_sell_trend(dataframe: DataFrame, metadata: dict) -> DataFrame:
            conditions = []

            # GUARDS AND TRENDS
            if params.get("sell-ema-high-enabled"):
                conditions.append(dataframe["open"] >= dataframe["ema-high"])

            # TRIGGERS
            if "sell-trigger" in params:
                if params["sell-trigger"] == "sell-fastk":
                    conditions.append(
                        qtpylib.crossed_above(
                            dataframe["fastk"], params["sell-fastk-value"]
                        )
                    )
                if params["sell-trigger"] == "sell-fastd":
                    conditions.append(
                        qtpylib.crossed_above(
                            dataframe["fastd"], params["sell-fastd-value"]
                        )
                    )

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
            Integer(0, 100, name="sell-fastk-value"),
            Integer(0, 100, name="sell-fastd-value"),
            Categorical([True, False], name="sell-ema-high-enabled"),
            Categorical([True, False], name="sell-fastk-enabled"),
            Categorical([True, False], name="sell-fastd-enabled"),
            Categorical(["sell-fastk", "sell-fastd"], name="sell-trigger"),
        ]
