import tools
from tools import search_listings, suggest_outfit, create_fit_card
from utils.data_loader import get_empty_wardrobe
import os
import sys

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

class FakeMessage:
    def __init__(self, content):
        self.content = content


class FakeChoice:
    def __init__(self, content):
        self.message = FakeMessage(content)


class FakeResponse:
    def __init__(self, content):
        self.choices = [FakeChoice(content)]


class FakeCompletions:
    def __init__(self, content):
        self.content = content

    def create(self, **kwargs):
        return FakeResponse(self.content)


class FakeChat:
    def __init__(self, content):
        self.completions = FakeCompletions(content)


class FakeClient:
    def __init__(self, content):
        self.chat = FakeChat(content)


def test_search_returns_results():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    assert isinstance(results, list)
    assert len(results) > 0


def test_search_empty_results():
    results = search_listings("designer ballgown", size="XXS", max_price=5)
    assert results == []


def test_search_price_filter():
    results = search_listings("jacket", size=None, max_price=10)
    assert all(item["price"] <= 10 for item in results)


def test_suggest_outfit_empty_wardrobe(monkeypatch):
    monkeypatch.setattr(
        tools,
        "_get_groq_client",
        lambda: FakeClient("Style it with baggy jeans and chunky sneakers for a casual streetwear look.")
    )

    results = search_listings("vintage graphic tee", size=None, max_price=50)
    outfit = suggest_outfit(results[0], get_empty_wardrobe())

    assert isinstance(outfit, str)
    assert outfit.strip() != ""
    assert "jeans" in outfit.lower() or "sneakers" in outfit.lower()


def test_create_fit_card_empty_outfit():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    caption = create_fit_card("", results[0])

    assert isinstance(caption, str)
    assert "outfit suggestion" in caption.lower()


def test_create_fit_card_success(monkeypatch):
    monkeypatch.setattr(
        tools,
        "_get_groq_client",
        lambda: FakeClient("Thrifted this tee off Depop for $24 and styled it with baggy jeans and sneakers.")
    )

    results = search_listings("vintage graphic tee", size=None, max_price=50)
    caption = create_fit_card("Pair it with baggy jeans and sneakers.", results[0])

    assert isinstance(caption, str)
    assert caption.strip() != ""
    assert "depop" in caption.lower() or "$" in caption
