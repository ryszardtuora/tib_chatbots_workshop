# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests
import pandas

CURRENCY_API = "http://api.nbp.pl/api/exchangerates/tables/A/"


class ActionGetCurrencyRates(Action):

    def name(self) -> Text:
        # this name must match the one specified in domain.yml and rules.yml
        return "action_get_currency_rates"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        response = requests.get(CURRENCY_API)
        rates_data = response.json()[0]["rates"]
        currencies = ["USD", "EUR", "GBP", "JPY"]
        df = pandas.DataFrame(rates_data)
        df = df[df["code"].isin(currencies)]
        df["mid"] = df["mid"].apply(lambda x: round(x,2))
        df = df[["code", "mid"]]
        table = df.to_html(index=False)
        dispatcher.utter_message(text=table)
        return []

