import asyncio
import json
import pytest
from app.config import Settings
from app.provider import GeminiProvider, ProviderError, make_provider


def test_gemini_selection():
    settings = Settings(provider='gemini', gemini_api_key='fake')
    assert isinstance(make_provider(settings), GeminiProvider)
    assert settings.embedding_model == 'gemini-embedding-001'


def test_gemini_embedding_tasks_and_order():
    class Fake(GeminiProvider):
        async def _post(self, route, payload):
            assert route.endswith(':batchEmbedContents')
            self.requests = payload['requests']
            return {'embeddings': [{'values': [1, 2]}, {'values': [3, 4]}]}
    p = Fake('fake')
    assert asyncio.run(p.embed_documents(['a', 'b'], 'm')) == [[1, 2], [3, 4]]
    assert all(r['taskType'] == 'RETRIEVAL_DOCUMENT' for r in p.requests)
    asyncio.run(p.embed(['a', 'b'], 'm'))
    assert all(r['taskType'] == 'RETRIEVAL_QUERY' for r in p.requests)


@pytest.mark.parametrize('data', [{'embeddings': []}, {'embeddings': [{'values': [True]}]}, {'embeddings': [{'values': [float('nan')]}]}, {}])
def test_gemini_bad_vectors(data):
    class Fake(GeminiProvider):
        async def _post(self, route, payload):
            return data
    with pytest.raises(ProviderError):
        asyncio.run(Fake('fake').embed(['a'], 'm'))


def test_gemini_answer_contract():
    class Fake(GeminiProvider):
        async def _post(self, route, payload):
            assert route.endswith(':generateContent')
            assert payload['generationConfig']['responseMimeType'] == 'application/json'
            assert 'untrusted' in payload['systemInstruction']['parts'][0]['text']
            return {'candidates': [{'finishReason': 'STOP', 'content': {'parts': [{'text': json.dumps({'answerable': False, 'claims': []})}]}}]}
    assert asyncio.run(Fake('fake').answer('q', [], 'm')) == {'answerable': False, 'claims': []}


@pytest.mark.parametrize('data', [{'candidates': []}, {'candidates': [{'finishReason': 'MAX_TOKENS'}]}, {}])
def test_gemini_incomplete_answers(data):
    class Fake(GeminiProvider):
        async def _post(self, route, payload):
            return data
    with pytest.raises(ProviderError):
        asyncio.run(Fake('fake').answer('q', [], 'm'))
