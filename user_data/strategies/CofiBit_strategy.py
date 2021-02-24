# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# isort: skip_file
from pandas import DataFrame
from freqtrade.strategy.interface import IStrategy

import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib


class CofiBitStrategy(IStrategy):
    """
    taken from slack by user CofiBit
    """

    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi"
    minimal_roi = {"0": 0.13419, "118": 0.07671, "220": 0.04869, "540": 0}

    # Optimal stoploss designed for the strategy
    # This attribute will be overridden if the config file contains "stoploss"
    stoploss = -0.20921

    # Optimal timeframe for the strategy
    timeframe = "5m"

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        stoch_fast = ta.STOCHF(dataframe, 5, 3, 0, 3, 0)
        dataframe["fastk"] = stoch_fast["fastk"]
        dataframe["fastd"] = stoch_fast["fastd"]
        dataframe["ema-high"] = ta.EMA(dataframe, timeperiod=5, price="high")
        dataframe["ema-low"] = ta.EMA(dataframe, timeperiod=5, price="low")
        dataframe["adx"] = ta.ADX(dataframe)

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the buy signal for the given dataframe
        :param dataframe: DataFrame
        :return: DataFrame with buy column
        """
        dataframe.loc[
            (
                (dataframe["open"] < dataframe["ema-low"])
                & (dataframe["fastk"] < 19)
                & (dataframe["fastd"] < 32)
                & (dataframe["adx"] > 12)
                & (qtpylib.crossed_above(dataframe["fastk"], dataframe["fastd"]))
                & (dataframe["volume"] > 0)
            ),
            "buy",
        ] = 1

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the sell signal for the given dataframe
        :param dataframe: DataFrame
        :return: DataFrame with buy column
        """

        dataframe.loc[
            (
                (dataframe["open"] >= dataframe["ema-high"])
                & (qtpylib.crossed_above(dataframe["fastk"], 70))
                & (qtpylib.crossed_above(dataframe["fastd"], 70))
            ),
            "sell",
        ] = 1

        return dataframe
