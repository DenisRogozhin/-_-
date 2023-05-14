import requests
import json
from collections import defaultdict
from typing import Dict, Any


class Model:
    def __init__(self, model: str = "model=russian-gsd-ud-2.10-220711"):
        self.api = "http://lindat.mff.cuni.cz/services/udpipe/api/process?"
        self.tokenizer = "tokenizer&"
        self.tagger = "tagger&"
        self.parser = "parser&"
        self.model = model + "&"

    def get_response(
            self,
            message: str,
            tokenizer: bool = True,
            tagger: bool = True,
            parser: bool = True,
            model: bool = True
    ) -> str:
        url = self.api
        if tokenizer:
            url += self.tokenizer
        if tagger:
            url += self.tagger
        if parser:
            url += self.parser
        if model:
            url += self.model

        url += f"data={message}"
        response_api = requests.get(url)
        data = response_api.text
        parse_json = json.loads(data)
        return parse_json["result"]

    def parse_result(self, response_result: str) -> Dict[str, Any]:
        answer_dict = {
            "lemmas": [],
            "main_words": [],
            "connections": [],
            "matches": []
        }
        lemmas = []
        connections = defaultdict(list)
        matches = {}
        for row in response_result.split('\n'):
            row_split = row.split()
            if row_split and row_split[0] != "#":
                num = row_split[0]
                parent = row_split[-4]
                lemma = row_split[2]
                lemmas.append(lemma)
                connections[parent].append(num)
                matches[num] = lemma
            elif lemmas:
                main_words = []
                for parent, children in connections.items():
                    if len(children) > 1:
                        main_words.append(matches[parent])

                answer_dict["lemmas"].append(lemmas)
                answer_dict["main_words"].append(main_words)
                answer_dict["connections"].append(connections)
                answer_dict["matches"].append(matches)

                connections = defaultdict(list)
                matches = {}
                lemmas = []
        return answer_dict
