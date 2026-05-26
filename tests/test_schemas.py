import pytest
from datetime import datetime
from pydantic import ValidationError

from src.schemas.wordbook import (
    WordBookCreate,
    WordBookRead,
    WordBookUpdate,
    WordBookListResponse,
)

from src.schemas.vocab_word import (
    VocabWordCreate,
    VocabWordRead,
    VocabWordUpdate,
    VocabWordListResponse,
)


# =========================
# WordBook schema tests
# =========================

def test_wordbook_create_valid():
    payload = WordBookCreate(
        name="N5 Vocabulary",
        description="Basic JLPT N5 words"
    )

    assert payload.name == "N5 Vocabulary"
    assert payload.description == "Basic JLPT N5 words"


def test_wordbook_create_rejects_empty_name():
    with pytest.raises(ValidationError):
        WordBookCreate(name="", description="Invalid")


def test_wordbook_create_rejects_long_name():
    with pytest.raises(ValidationError):
        WordBookCreate(name="a" * 101)


def test_wordbook_update_allows_partial_update():
    payload = WordBookUpdate(description="Updated description")

    assert payload.name is None
    assert payload.description == "Updated description"


def test_wordbook_update_rejects_empty_name():
    with pytest.raises(ValidationError):
        WordBookUpdate(name="")


def test_wordbook_read_requires_positive_id():
    with pytest.raises(ValidationError):
        WordBookRead(
            id=0,
            name="N5 Vocabulary",
            description="Basic words",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )


def test_wordbook_list_response_accepts_items():
    wordbook = WordBookRead(
        id=1,
        name="N5 Vocabulary",
        description="Basic words",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    response = WordBookListResponse(items=[wordbook])

    assert response.items[0].id == 1
    assert response.items[0].name == "N5 Vocabulary"


# =========================
# VocabWord schema tests
# =========================

def test_vocab_word_create_valid():
    payload = VocabWordCreate(
        wordbook_id=1,
        word="食べる",
        hiragana="たべる",
        jlpt_level="N5",
        part_of_speech="verb",
        meaning_zh="吃",
    )

    assert payload.wordbook_id == 1
    assert payload.word == "食べる"
    assert payload.hiragana == "たべる"
    assert payload.jlpt_level == "N5"
    assert payload.part_of_speech == "verb"
    assert payload.meaning_zh == "吃"


def test_vocab_word_create_allows_empty_hiragana():
    payload = VocabWordCreate(
        wordbook_id=1,
        word="ホテル",
        hiragana=None,
        jlpt_level="N5",
        part_of_speech="noun",
        meaning_zh="飯店",
    )

    assert payload.hiragana is None


def test_vocab_word_create_rejects_invalid_wordbook_id():
    with pytest.raises(ValidationError):
        VocabWordCreate(
            wordbook_id=0,
            word="食べる",
            hiragana="たべる",
            jlpt_level="N5",
            part_of_speech="verb",
            meaning_zh="吃",
        )


def test_vocab_word_create_rejects_empty_word():
    with pytest.raises(ValidationError):
        VocabWordCreate(
            wordbook_id=1,
            word="",
            hiragana="たべる",
            jlpt_level="N5",
            part_of_speech="verb",
            meaning_zh="吃",
        )


def test_vocab_word_create_rejects_invalid_jlpt_level():
    with pytest.raises(ValidationError):
        VocabWordCreate(
            wordbook_id=1,
            word="食べる",
            hiragana="たべる",
            jlpt_level="N9",
            part_of_speech="verb",
            meaning_zh="吃",
        )


def test_vocab_word_create_rejects_invalid_part_of_speech():
    with pytest.raises(ValidationError):
        VocabWordCreate(
            wordbook_id=1,
            word="食べる",
            hiragana="たべる",
            jlpt_level="N5",
            part_of_speech="wrong_type",
            meaning_zh="吃",
        )


def test_vocab_word_create_rejects_empty_meaning():
    with pytest.raises(ValidationError):
        VocabWordCreate(
            wordbook_id=1,
            word="食べる",
            hiragana="たべる",
            jlpt_level="N5",
            part_of_speech="verb",
            meaning_zh="",
        )


def test_vocab_word_update_allows_partial_update():
    payload = VocabWordUpdate(meaning_zh="吃、食用")

    assert payload.meaning_zh == "吃、食用"
    assert payload.word is None


def test_vocab_word_read_requires_positive_id():
    with pytest.raises(ValidationError):
        VocabWordRead(
            id=0,
            wordbook_id=1,
            word="食べる",
            hiragana="たべる",
            jlpt_level="N5",
            part_of_speech="verb",
            meaning_zh="吃",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )


def test_vocab_word_list_response_accepts_items():
    word = VocabWordRead(
        id=1,
        wordbook_id=1,
        word="食べる",
        hiragana="たべる",
        jlpt_level="N5",
        part_of_speech="verb",
        meaning_zh="吃",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    response = VocabWordListResponse(items=[word])

    assert response.items[0].id == 1
    assert response.items[0].word == "食べる"