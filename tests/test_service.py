from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models.wordbook import WordBook
from src.models.vocab_word import VocabWord
from src.schemas.wordbook import WordBookCreate, WordBookUpdate
from src.schemas.vocab_word import VocabWordCreate, VocabWordUpdate
from src.services import wordbook_service, vocab_service, quiz_service


def make_query(first=None, all_=None):
    query = MagicMock()
    query.filter.return_value = query
    query.order_by.return_value = query
    query.first.return_value = first
    query.all.return_value = [] if all_ is None else all_
    return query


# WordBook service tests
def test_get_wordbook_or_404_returns_wordbook():
    wordbook = WordBook(id=1, name="N5 Vocabulary", description="Basic words")

    db = MagicMock(spec=Session)
    db.query.return_value = make_query(first=wordbook)

    result = wordbook_service.get_wordbook_or_404(db=db, wordbook_id=1)

    assert result is wordbook


def test_get_wordbook_or_404_missing_raises():
    db = MagicMock(spec=Session)
    db.query.return_value = make_query(first=None)

    with pytest.raises(HTTPException) as excinfo:
        wordbook_service.get_wordbook_or_404(db=db, wordbook_id=99)

    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "WordBook not found"


def test_create_wordbook_commits_and_returns_wordbook():
    db = MagicMock(spec=Session)
    db.query.return_value = make_query(first=None)

    payload = WordBookCreate(
        name="N5 Vocabulary",
        description="Basic JLPT N5 words"
    )

    result = wordbook_service.create_wordbook(db=db, payload=payload)

    assert isinstance(result, WordBook)
    assert result.name == "N5 Vocabulary"
    assert result.description == "Basic JLPT N5 words"

    db.add.assert_called_once_with(result)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)


def test_create_wordbook_duplicate_name_raises():
    existing_wordbook = WordBook(
        id=1,
        name="N5 Vocabulary",
        description="Already exists"
    )

    db = MagicMock(spec=Session)
    db.query.return_value = make_query(first=existing_wordbook)

    payload = WordBookCreate(
        name="N5 Vocabulary",
        description="Duplicate"
    )

    with pytest.raises(HTTPException) as excinfo:
        wordbook_service.create_wordbook(db=db, payload=payload)

    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "WordBook name already exists"


def test_list_wordbooks_returns_wordbooks():
    wordbooks = [
        WordBook(id=2, name="N4 Vocabulary", description="N4 words"),
        WordBook(id=1, name="N5 Vocabulary", description="N5 words"),
    ]

    db = MagicMock(spec=Session)
    db.query.return_value = make_query(all_=wordbooks)

    result = wordbook_service.list_wordbooks(db=db)

    assert result == wordbooks


def test_update_wordbook_no_fields_raises():
    wordbook = WordBook(id=1, name="N5 Vocabulary", description="Old")

    db = MagicMock(spec=Session)
    db.query.return_value = make_query(first=wordbook)

    with pytest.raises(HTTPException) as excinfo:
        wordbook_service.update_wordbook(
            db=db,
            wordbook_id=1,
            payload=WordBookUpdate(),
        )

    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "No fields to update"


def test_update_wordbook_updates_fields():
    wordbook = WordBook(id=1, name="N5 Vocabulary", description="Old")

    # 第一次 query：get_wordbook_or_404 找到原本 wordbook
    # 第二次 query：檢查新 name 是否重複，回傳 None 代表沒有重複
    db = MagicMock(spec=Session)
    db.query = MagicMock(
        side_effect=[
            make_query(first=wordbook),
            make_query(first=None),
        ]
    )

    payload = WordBookUpdate(name="Updated N5", description="Updated")

    result = wordbook_service.update_wordbook(
        db=db,
        wordbook_id=1,
        payload=payload,
    )

    assert result is wordbook
    assert wordbook.name == "Updated N5"
    assert wordbook.description == "Updated"

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(wordbook)


def test_delete_wordbook_deletes_and_commits():
    wordbook = WordBook(id=1, name="N5 Vocabulary", description="Basic words")

    db = MagicMock(spec=Session)
    db.query.return_value = make_query(first=wordbook)

    wordbook_service.delete_wordbook(db=db, wordbook_id=1)

    db.delete.assert_called_once_with(wordbook)
    db.commit.assert_called_once()


# VocabWord service tests
def test_create_vocab_word_commits_and_returns_word():
    wordbook = WordBook(id=1, name="N5 Vocabulary", description="Basic words")

    db = MagicMock(spec=Session)
    db.query.return_value = make_query(first=wordbook)

    payload = VocabWordCreate(
        wordbook_id=1,
        word="食べる",
        hiragana="たべる",
        jlpt_level="N5",
        part_of_speech="verb",
        meaning_zh="吃",
    )

    result = vocab_service.create_vocab_word(db=db, payload=payload)

    assert isinstance(result, VocabWord)
    assert result.wordbook_id == 1
    assert result.word == "食べる"
    assert result.hiragana == "たべる"
    assert result.jlpt_level == "N5"
    assert result.part_of_speech == "verb"
    assert result.meaning_zh == "吃"

    db.add.assert_called_once_with(result)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)


def test_create_vocab_word_missing_wordbook_raises():
    db = MagicMock(spec=Session)
    db.query.return_value = make_query(first=None)

    payload = VocabWordCreate(
        wordbook_id=99,
        word="食べる",
        hiragana="たべる",
        jlpt_level="N5",
        part_of_speech="verb",
        meaning_zh="吃",
    )

    with pytest.raises(HTTPException) as excinfo:
        vocab_service.create_vocab_word(db=db, payload=payload)

    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "WordBook not found"


def test_list_vocab_words_returns_words():
    words = [
        VocabWord(
            id=1,
            wordbook_id=1,
            word="食べる",
            hiragana="たべる",
            jlpt_level="N5",
            part_of_speech="verb",
            meaning_zh="吃",
        ),
        VocabWord(
            id=2,
            wordbook_id=1,
            word="学校",
            hiragana="がっこう",
            jlpt_level="N5",
            part_of_speech="noun",
            meaning_zh="學校",
        ),
    ]

    db = MagicMock(spec=Session)
    db.query.return_value = make_query(all_=words)

    result = vocab_service.list_vocab_words(db=db)

    assert result == words


def test_get_vocab_word_or_404_missing_raises():
    db = MagicMock(spec=Session)
    db.query.return_value = make_query(first=None)

    with pytest.raises(HTTPException) as excinfo:
        vocab_service.get_vocab_word_or_404(db=db, word_id=99)

    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Vocab word not found"


def test_update_vocab_word_no_fields_raises():
    vocab_word = VocabWord(
        id=1,
        wordbook_id=1,
        word="食べる",
        hiragana="たべる",
        jlpt_level="N5",
        part_of_speech="verb",
        meaning_zh="吃",
    )

    db = MagicMock(spec=Session)
    db.query.return_value = make_query(first=vocab_word)

    with pytest.raises(HTTPException) as excinfo:
        vocab_service.update_vocab_word(
            db=db,
            word_id=1,
            payload=VocabWordUpdate(),
        )

    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "No fields to update"


def test_update_vocab_word_updates_fields():
    vocab_word = VocabWord(
        id=1,
        wordbook_id=1,
        word="食べる",
        hiragana="たべる",
        jlpt_level="N5",
        part_of_speech="verb",
        meaning_zh="吃",
    )

    db = MagicMock(spec=Session)
    db.query.return_value = make_query(first=vocab_word)

    payload = VocabWordUpdate(meaning_zh="吃、食用")

    result = vocab_service.update_vocab_word(
        db=db,
        word_id=1,
        payload=payload,
    )

    assert result is vocab_word
    assert vocab_word.meaning_zh == "吃、食用"

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(vocab_word)


def test_delete_vocab_word_deletes_and_commits():
    vocab_word = VocabWord(
        id=1,
        wordbook_id=1,
        word="食べる",
        hiragana="たべる",
        jlpt_level="N5",
        part_of_speech="verb",
        meaning_zh="吃",
    )

    db = MagicMock(spec=Session)
    db.query.return_value = make_query(first=vocab_word)

    vocab_service.delete_vocab_word(db=db, word_id=1)

    db.delete.assert_called_once_with(vocab_word)
    db.commit.assert_called_once()


# Quiz service tests
def test_quiz_service_rejects_empty_levels():
    db = MagicMock(spec=Session)

    with pytest.raises(HTTPException) as excinfo:
        quiz_service.get_quiz_words(db=db, levels=[])

    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "At least one JLPT level must be selected"


def test_quiz_service_rejects_invalid_level():
    db = MagicMock(spec=Session)

    with pytest.raises(HTTPException) as excinfo:
        quiz_service.get_quiz_words(db=db, levels=["N9"])

    assert excinfo.value.status_code == 400
    assert "Invalid JLPT level" in excinfo.value.detail


def test_quiz_service_returns_words_by_levels():
    words = [
        VocabWord(
            id=1,
            wordbook_id=1,
            word="食べる",
            hiragana="たべる",
            jlpt_level="N5",
            part_of_speech="verb",
            meaning_zh="吃",
        )
    ]

    db = MagicMock(spec=Session)
    db.query.return_value = make_query(all_=words)

    result = quiz_service.get_quiz_words(db=db, levels=["N5"])

    assert result == words


def test_create_vocab_word_commits_and_returns_word():
    wordbook = WordBook(id=1, name="N5 Vocabulary", description="Basic words")

    db = MagicMock(spec=Session)
    db.query = MagicMock(
        side_effect=[
            make_query(first=wordbook),  # get_wordbook_or_404：單字本存在
            make_query(first=None),      # check_duplicate_word：沒有重複單字
        ]
    )

    payload = VocabWordCreate(
        wordbook_id=1,
        word="食べる",
        hiragana="たべる",
        jlpt_level="N5",
        part_of_speech="verb",
        meaning_zh="吃",
    )

    result = vocab_service.create_vocab_word(db=db, payload=payload)

    assert isinstance(result, VocabWord)
    assert result.wordbook_id == 1
    assert result.word == "食べる"
    assert result.hiragana == "たべる"
    assert result.jlpt_level == "N5"
    assert result.part_of_speech == "verb"
    assert result.meaning_zh == "吃"

    db.add.assert_called_once_with(result)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)

def test_update_vocab_word_duplicate_word_raises():
    vocab_word = VocabWord(
        id=1,
        wordbook_id=1,
        word="飲む",
        hiragana="のむ",
        jlpt_level="N5",
        part_of_speech="verb",
        meaning_zh="喝",
    )

    existing_word = VocabWord(
        id=2,
        wordbook_id=1,
        word="食べる",
        hiragana="たべる",
        jlpt_level="N5",
        part_of_speech="verb",
        meaning_zh="吃",
    )

    db = MagicMock(spec=Session)
    db.query = MagicMock(
        side_effect=[
            make_query(first=vocab_word),     # get_vocab_word_or_404
            make_query(first=existing_word),  # check_duplicate_word
        ]
    )

    payload = VocabWordUpdate(word="食べる")

    with pytest.raises(HTTPException) as excinfo:
        vocab_service.update_vocab_word(
            db=db,
            word_id=1,
            payload=payload,
        )

    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Word already exists in this wordbook"