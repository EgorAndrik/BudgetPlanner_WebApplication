from _decimal import Decimal
from pycbrf.toolbox import ExchangeRates


class CurrencyExchanger:
    def __init__(self, currency: list):
        self.dataCurrencyForBank = currency

    def exchange(self, date: str):
        return [float(round(self._get_currency_rate(date, i), 2)) for i in self.dataCurrencyForBank]

    def _get_currency_rate(self, date: str, currency: str) -> Decimal:
        rates = ExchangeRates(date)
        return rates[currency].value


# bank = CurrencyExchanger(currency=['USD', 'EUR', 'CNY'])
#
# print(bank.exchange(date='2023-09-01'))
# >>> [96.33, 104.94, 13.19] rub
