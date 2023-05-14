from src.udpipe import Model


def test_udpipe():
    model = Model()
    response = model.get_response("Всем привет! Я люблю заниматься программировнием, особенно NLP.")
    result = model.parse_result(response)
    assert ' '.join(result["lemmas"][1]) == "любить NLP"
