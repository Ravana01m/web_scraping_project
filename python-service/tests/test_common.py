"""Tests for common utilities — character conversion and review normalization."""

import pytest
from scraper.common import build_review_dict, normalize_review_text


class TestCharacterConversion:
    """Verify that list(review) is used, NOT split()."""

    def test_basic_text(self):
        result = build_review_dict(rating="5", review_text="Hello")
        assert result["review_characters"] == ["H", "e", "l", "l", "o"]

    def test_spaces_preserved(self):
        result = build_review_dict(rating="5", review_text="a b c")
        assert result["review_characters"] == ["a", " ", "b", " ", "c"]

    def test_punctuation_preserved(self):
        result = build_review_dict(rating="5", review_text="Hello!")
        assert result["review_characters"] == ["H", "e", "l", "l", "o", "!"]

    def test_emojis_preserved(self):
        text = "Great! 🎉"
        result = build_review_dict(rating="5", review_text=text)
        chars = result["review_characters"]
        assert "🎉" in chars
        assert " " in chars

    def test_numbers_preserved(self):
        result = build_review_dict(rating="5", review_text="Score: 10/10")
        chars = result["review_characters"]
        assert "1" in chars
        assert "0" in chars
        assert "/" in chars

    def test_special_characters(self):
        result = build_review_dict(rating="5", review_text="A&B@C#D$E")
        chars = result["review_characters"]
        assert "&" in chars
        assert "@" in chars
        assert "#" in chars
        assert "$" in chars

    def test_capitalization_preserved(self):
        result = build_review_dict(rating="5", review_text="AbCdEf")
        assert result["review_characters"] == ["A", "b", "C", "d", "E", "f"]

    def test_character_order_preserved(self):
        text = "This phone is excellent!"
        result = build_review_dict(rating="5", review_text=text)
        assert result["review_characters"] == list(text)

    def test_empty_text(self):
        result = build_review_dict(rating="5", review_text="")
        assert result["review_characters"] == []
        assert result["review"] == ""

    def test_review_and_characters_consistent(self):
        """Verify review_characters == list(review)."""
        text = "Test review 123!"
        result = build_review_dict(rating="4", review_text=text)
        assert result["review_characters"] == list(result["review"])


class TestNormalizeReviewText:
    def test_collapse_whitespace(self):
        assert normalize_review_text("hello   world") == "hello world"

    def test_strip_edges(self):
        assert normalize_review_text("  hello  ") == "hello"

    def test_newlines_to_space(self):
        assert normalize_review_text("line1\nline2") == "line1 line2"

    def test_tabs_to_space(self):
        assert normalize_review_text("a\t\tb") == "a b"


class TestBuildReviewDict:
    def test_all_fields(self):
        result = build_review_dict(
            rating="5", review_text="Great product", likes="10", dislikes="2"
        )
        assert result["rating"] == "5"
        assert result["review"] == "Great product"
        assert result["likes"] == "10"
        assert result["dislikes"] == "2"
        assert result["review_characters"] == list("Great product")

    def test_none_fields(self):
        result = build_review_dict(rating=None, review_text="Text")
        assert result["rating"] is None
        assert result["likes"] is None
        assert result["dislikes"] is None
