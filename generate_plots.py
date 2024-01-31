import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import generate_table

class Plots:
    def __init__ (self, directory):
        self.table = generate_table.new_database(directory)
        self.prices = [[]]
        self.offset = 0
    
    # Auxiliary tables used by the plots ==================================================================================
    
    def __relative(self):
        df = self.table.copy(deep=True)
        before = df.iloc[0]
        for row in range(1, len(df.index)):
            now = df.iloc[row]
            df.iloc[row] = before - now
            before = now
        df.drop(df.index[0], inplace=True)
        return df

    def __permonth(self, dropna=False):
        df = self.__relative()
        if dropna:
            df.dropna(inplace=True)
        df.index = pd.to_datetime(df.index) - pd.Timedelta(days=15)
        df = df.resample("M").sum()
        df.clip(lower=0, inplace=True)
        df.index = df.index.strftime("%Y-%m")
        df.index.rename("Month", inplace=True)
        return df

    def __prices(self):
        df = self.__permonth()
        df.insert(0, "Year", pd.DatetimeIndex(df.index).year)
        df.reset_index(inplace=True)
        df.set_index("Year", inplace=True)
        df.insert(1, "Vazio", df["csv"] * self.prices["Vazio"])
        df.insert(2, "Ponta", df["csp"] * self.prices["Ponta"])
        df.insert(3, "Cheias", df["csc"] * self.prices["Cheias"])
        df.drop(["ccv", "csv", "ccp", "csp", "ccc", "csc", "icv", "isv", "icp", "isp", "icc", "isc"], axis=1, inplace=True)
        df.set_index("Month", inplace=True)
        return df
    
    
    # Setters =============================================================================================================

    def set_prices(self, list):
        """Create a list with the prices of each tariff
        
        Args:
            list (list<list<int>>): List of prices: Year, "Vazio", "Ponta", "Cheias"
        """
        df = pd.DataFrame(list, columns=["Year", "Vazio", "Ponta", "Cheias"])
        df.set_index("Year", inplace=True)
        self.prices = df
        
    def set_turning_day(self, day):
        """Set the turning day of the month
        
        Args:
            day (int): The day of the month
        """
        self.offset = day


    # Plots ===============================================================================================================

    def execute(self):
        """Execute all the plots"""
        self.E1()
        self.E2()
        self.E3()
        self.E4()
        self.P1()
        self.P2()
        self.P3()
        self.N1()
    
    def E1(self):
        """Energy consumed and injected per month"""
        df = self.__permonth()
        df.insert(1, "Consumido", df["csv"] + df["csp"] + df["csc"])
        df.insert(2, "Injetado", df["isv"] + df["isp"] + df["isc"])
        df.drop(["ccv", "csv", "ccp", "csp", "ccc", "csc", "icv", "isv", "icp", "isp", "icc", "isc"], axis=1, inplace=True)

        df.plot(kind="area", stacked=False, xlabel="Mês", ylabel="KWh", title="Energia consumida e injetada")
        plt.show()

    def E2(self):
        """Energy consumed in each month, compared between years"""
        df = self.__permonth()
        df.insert(1, "KWh consumidos", df["csv"] + df["csp"] + df["csc"])
        df.drop(["ccv", "csv", "ccp", "csp", "ccc", "csc", "icv", "isv", "icp", "isp", "icc", "isc"], axis=1, inplace=True)
        df.insert(0, "Mês", pd.DatetimeIndex(df.index).month)
        df.insert(1, "Ano", pd.DatetimeIndex(df.index).year)
        df = df.pivot_table(index="Mês", columns="Ano", values="KWh consumidos", aggfunc="sum")

        df.plot(kind="bar", stacked=False, xlabel="Mês", ylabel="KWh", title="Energia consumida (comparada entre anos)")
        plt.show()

    def E3(self):
        """Energy consumed per month and for each tariff (in KWh)"""
        df = self.__permonth()
        df.drop(["ccv", "ccp", "ccc", "icv", "isv", "icp", "isp", "icc", "isc"], axis=1, inplace=True)
        df.rename(columns={"csv": "Vazio", "csp": "Ponta", "csc": "Cheias"}, inplace=True)

        df.plot(kind="area", stacked=True, xlabel="Mês", ylabel="KWh", title="Energia consumida por tarifa (em KWh)")
        plt.show()

    def E4(self):
        """Energy consumed per month and for each tariff (in percentage)"""
        df = self.__permonth()
        df.drop(["ccv", "ccp", "ccc", "icv", "isv", "icp", "isp", "icc", "isc"], axis=1, inplace=True)
        df.rename(columns={"csv": "Vazio", "csp": "Ponta", "csc": "Cheias"}, inplace=True)
        df = df.div(df.sum(axis=1), axis=0).mul(100)
        
        df.plot(kind="bar", stacked=True, xlabel="Mês", ylabel="%", title="Energia consumida por tarifa (em %)")
        plt.axhline(y=75, color="white", linestyle='-')
        plt.show()

    def P1(self):
        """Price and energy consumed per month"""
        df = self.__prices()
        df.insert(1, "Preço (sem impostos)", df["Vazio"] + df["Ponta"] + df["Cheias"])
        df.drop(["Vazio", "Ponta", "Cheias"], axis=1, inplace=True)

        kw = self.__permonth()
        kw.insert(0, "Consumo elétrico", kw["csv"] + kw["csp"] + kw["csc"])
        df.insert(1, "Consumo elétrico", kw["Consumo elétrico"])
        
        df.plot(kind="area", stacked=False, xlabel="Mês", ylabel="€ ou KWh", title="Preço e energia consumida")
        plt.show()
        
    def P2(self):
        """Price for each tariff per month"""
        df = self.__prices()
        
        df.plot(kind="area", stacked=True, xlabel="Mês", ylabel="€", title="Preço por tarifa")
        plt.show()
        
    def P3(self):
        """Price for each month, compared between years"""
        df = self.__prices()
        df.insert(1, "Preço (sem impostos)", df["Vazio"] + df["Ponta"] + df["Cheias"])
        df.drop(["Vazio", "Ponta", "Cheias"], axis=1, inplace=True)
        df.insert(0, "Mês", pd.DatetimeIndex(df.index).month)
        df.insert(1, "Ano", pd.DatetimeIndex(df.index).year)
        df = df.pivot_table(index="Mês", columns="Ano", values="Preço (sem impostos)", aggfunc="sum")
        
        df.plot(kind="bar", stacked=False, xlabel="Mês", ylabel="€", title="Preço estimado (comparado entre anos)")
        plt.show()

    def N1(self):
        """Energy saved per month, thanks to Net Metering"""
        df = self.__permonth(True)
        df.insert(0, "Vazio", df["ccv"] - df["csv"])
        df.insert(1, "Ponta", df["ccp"] - df["csp"])
        df.insert(2, "Cheias", df["ccc"] - df["csc"])
        df.clip(lower=0, inplace=True)
        df.drop(["ccv", "csv", "ccp", "csp", "ccc", "csc", "icv", "isv", "icp", "isp", "icc", "isc"], axis=1, inplace=True)

        df.plot(kind="area", stacked=True, xlabel="Mês", ylabel="KWh", title="Energia poupada graças ao Net Metering")
        plt.show()
