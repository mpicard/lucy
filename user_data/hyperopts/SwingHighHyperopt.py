# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement

import talib.abstract as ta
from pandas import DataFrame
from typing import Dict, Any, Callable, List
from functools import reduce

import numpy as np
from skopt.space import Categorical, Dimension, Integer, Real
import freqtrade.vendor.qtpylib.indicators as qtpylib
from freqtrade.optimize.hyperopt_interface import IHyperOpt


cciTimeMin = 10
cciTimeMax = 100
cciValueMin = -400
cciValueMax = 400
cciTimeRange = range(cciTimeMin, cciTimeMax)


class SwingHighHyperopt(IHyperOpt):
    @staticmethod
    def populate_indicators(dataframe: DataFrame, metadata: dict) -> DataFrame:
        macd = ta.MACD(dataframe)
        dataframe["macd"] = macd["macd"]
        dataframe["macdsignal"] = macd["macdsignal"]

        for cciTime in cciTimeRange:
            cciName = "cci-" + str(cciTime)
            dataframe[cciName] = ta.CCI(dataframe, timeperiod=cciTime)

        return dataframe

    @staticmethod
    def buy_strategy_generator(params: Dict[str, Any]) -> Callable:
        def populate_buy_trend(dataframe: DataFrame, metadata: dict) -> DataFrame:

            conditions = []

            # TRIGGERS & GUARDS
            if "trigger" in params:
                for cciTime in cciTimeRange:
                    cciName = "cci-" + str(cciTime)
                    if params["trigger"] == cciName:
                        conditions.append(dataframe[cciName] < params["buy-cci-value"])
                        conditions.append(dataframe["macd"] > dataframe["macdsignal"])
            conditions.append(dataframe["volume"] > 0)

            if conditions:
                dataframe.loc[reduce(lambda x, y: x & y, conditions), "buy"] = 1

            return dataframe

        return populate_buy_trend

    @staticmethod
    def indicator_space() -> List[Dimension]:
        indicators = []

        for cciTime in cciTimeRange:
            cciName = "cci-" + str(cciTime)
            indicators.append(cciName)

        return [
            Integer(cciValueMin, cciValueMax, name="buy-cci-value"),
            Categorical(indicators, name="trigger"),
        ]

    @staticmethod
    def sell_strategy_generator(params: Dict[str, Any]) -> Callable:
        def populate_sell_trend(dataframe: DataFrame, metadata: dict) -> DataFrame:

            conditions = []

            # TRIGGERS & GUARDS
            if "sell-trigger" in params:
                for cciTime in cciTimeRange:
                    cciName = "cci-" + str(cciTime)
                    if params["sell-trigger"] == cciName:
                        conditions.append(dataframe[cciName] > params["sell-cci-value"])
                        conditions.append(dataframe["macd"] < dataframe["macdsignal"])
            conditions.append(dataframe["volume"] > 0)

            if conditions:
                dataframe.loc[reduce(lambda x, y: x & y, conditions), "sell"] = 1

            return dataframe

        return populate_sell_trend

    @staticmethod
    def sell_indicator_space() -> List[Dimension]:
        indicators = []

        for cciTime in cciTimeRange:
            cciName = "cci-" + str(cciTime)
            indicators.append(cciName)

        return [
            Integer(cciValueMin, cciValueMax, name="sell-cci-value"),
            Categorical(indicators, name="sell-trigger"),
        ]
