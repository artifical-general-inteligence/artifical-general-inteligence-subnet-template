import requests
import json


class OllamaClient:
    def __init__(self, url="http://ollama.hyperclouds.io:31434/api"):
        self.base_url = url

    def show(self, model_name):
        """
        Show information about a model including details, modelfile, template, parameters, license, system prompt.
        :param model_name:
        :return:
        """
        url = f"{self.base_url}/show"
        payload = {"name": model_name}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        return response.json()

    def ps(self):
        """
        List models that are currently loaded into memory.
        :return:
        """
        url = f"{self.base_url}/ps"
        response = requests.get(url)
        return response.json()

    def tags(self):
        """
        List models that are available locally.
        :return:
        """
        url = f"{self.base_url}/tags"
        response = requests.get(url)
        return response.json()