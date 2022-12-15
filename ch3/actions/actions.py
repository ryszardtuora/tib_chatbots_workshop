# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import requests
import pandas

CURRENCY_API = "http://api.nbp.pl/api/exchangerates/tables/A/"
DUCKLING_API = "http://0.0.0.0:8000/parse"


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
        #table = df.to_markdown(index=False)
        table = df.to_html(index=False)
        dispatcher.utter_message(text=table)
        return []


class ActionGetMonetary(Action):
    def name(self) -> Text:
        return "action_get_monetary_amount"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        message = tracker.latest_message["text"]
        duckling_output = requests.post(DUCKLING_API, data={"text": message}).json()
        monetary_entities = [ent for ent in duckling_output if ent["dim"] == "amount-of-money"]
        if monetary_entities:
            monetary_entity = monetary_entities[0]
            value = monetary_entity["value"]["value"]
            unit = monetary_entity["value"]["unit"]
            full_ent = f"{value} {unit}"
            slot_filling = SlotSet("monetary_amount", full_ent)
            return [slot_filling]

        return []

class ActionRunTransfer(Action):
    def name(self) -> Text:
        return "action_run_transfer"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        beneficiary = tracker.get_slot("beneficiary")
        monetary_amount = tracker.get_slot("monetary_amount")
        transfer_title = tracker.get_slot("transfer_title")
        message = f"Sending a transfer of {monetary_amount} to {beneficiary} with the title of {transfer_title}"
        dispatcher.utter_message(message)
        return [SlotSet("beneficiary", None), 
                SlotSet("monetary_amount", None),
                SlotSet("transfer_title", None)]
 
