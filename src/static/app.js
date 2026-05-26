const API = {
  wordbooks: "/wordbooks",
  words: "/words",
  quizWords: "/quiz/words",
};

const POS_LABELS = {
  noun: "名詞",
  verb: "動詞",
  i_adjective: "い形容詞",
  na_adjective: "な形容詞",
  adverb: "副詞",
  expression: "慣用語 / 表現",
  other: "其他",
};

let wordbooks = [];
let words = [];

let quizWords = [];
let quizIndex = 0;
let quizShowingMeaning = false;

const tabButtons = document.querySelectorAll(".nav-button");
const panels = document.querySelectorAll(".panel");

const wordbookStatus = document.querySelector("#wordbook-status");
const wordbookForm = document.querySelector("#wordbook-form");
const wordbookIdInput = document.querySelector("#wordbook-id");
const wordbookNameInput = document.querySelector("#wordbook-name");
const wordbookDescriptionInput = document.querySelector("#wordbook-description");
const clearWordbookButton = document.querySelector("#clear-wordbook-button");
const wordbookList = document.querySelector("#wordbook-list");

const wordStatus = document.querySelector("#word-status");
const wordForm = document.querySelector("#word-form");
const wordIdInput = document.querySelector("#word-id");
const wordWordbookSelect = document.querySelector("#word-wordbook-id");
const wordTextInput = document.querySelector("#word-text");
const wordHiraganaInput = document.querySelector("#word-hiragana");
const wordJlptSelect = document.querySelector("#word-jlpt-level");
const wordPartOfSpeechSelect = document.querySelector("#word-part-of-speech");
const wordMeaningInput = document.querySelector("#word-meaning");
const clearWordButton = document.querySelector("#clear-word-button");
const filterJlptSelect = document.querySelector("#filter-jlpt-level");
const wordList = document.querySelector("#word-list");

const quizStatus = document.querySelector("#quiz-status");
const startQuizButton = document.querySelector("#start-quiz-button");
const endQuizButton = document.querySelector("#end-quiz-button");
const quizCard = document.querySelector("#quiz-card");
const quizLevel = document.querySelector("#quiz-level");
const quizWord = document.querySelector("#quiz-word");
const quizHiragana = document.querySelector("#quiz-hiragana");
const quizMeaning = document.querySelector("#quiz-meaning");
const quizNextButton = document.querySelector("#quiz-next-button");

async function requestJson(url, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let detail = `Request failed with status ${response.status}`;
    try {
      const errorBody = await response.json();
      detail = errorBody.detail || detail;
    } catch {
      detail = response.statusText || detail;
    }
    throw new Error(detail);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

function setStatus(element, message) {
  element.textContent = message;
}

function switchTab(tabName) {
  tabButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.tab === tabName);
  });

  panels.forEach((panel) => {
    panel.classList.toggle("active", panel.id === `${tabName}-section`);
  });

  const sidebar = document.querySelector("#sidebar");
  sidebar.className = `sidebar sidebar-${tabName}`;
}

function getWordbookName(wordbookId) {
  const wordbook = wordbooks.find((item) => Number(item.id) === Number(wordbookId));
  return wordbook ? wordbook.name : `WordBook ${wordbookId}`;
}

function clearWordbookForm() {
  wordbookIdInput.value = "";
  wordbookNameInput.value = "";
  wordbookDescriptionInput.value = "";
  wordbookNameInput.focus();
}

function clearWordForm() {
  wordIdInput.value = "";
  wordTextInput.value = "";
  wordHiraganaInput.value = "";
  wordJlptSelect.value = "N5";
  wordPartOfSpeechSelect.value = "noun";
  wordMeaningInput.value = "";
  wordTextInput.focus();
}

async function loadWordbooks() {
  setStatus(wordbookStatus, "Loading...");

  try {
    const data = await requestJson(API.wordbooks);
    wordbooks = data.items || [];

    renderWordbooks();
    renderWordbookOptions();

    document.querySelector("#home-wordbook-count").textContent = wordbooks.length;

    setStatus(wordbookStatus, `${wordbooks.length} 個單字本`);
  } catch (error) {
    setStatus(wordbookStatus, error.message);
  }
}

function renderWordbookOptions() {
  wordWordbookSelect.textContent = "";

  if (wordbooks.length === 0) {
    const option = document.createElement("option");
    option.value = "";
    option.textContent = "請先建立單字本";
    wordWordbookSelect.appendChild(option);
    return;
  }

  wordbooks.forEach((wordbook) => {
    const option = document.createElement("option");
    option.value = wordbook.id;
    option.textContent = wordbook.name;
    wordWordbookSelect.appendChild(option);
  });
}

function renderWordbooks() {
  wordbookList.textContent = "";

  if (wordbooks.length === 0) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.textContent = "目前沒有單字本，請先新增一個。";
    wordbookList.appendChild(empty);
    return;
  }

  wordbooks.forEach((wordbook) => {
    const card = document.createElement("article");
    card.className = "item-card";

    card.innerHTML = `
      <div>
        <h3>${escapeHtml(wordbook.name)}</h3>
        <p>${escapeHtml(wordbook.description || "沒有描述")}</p>
      </div>
      <div class="item-actions">
        <button class="secondary-button" data-action="edit-wordbook" data-id="${wordbook.id}">編輯</button>
        <button class="danger-button" data-action="delete-wordbook" data-id="${wordbook.id}">刪除</button>
      </div>
    `;

    wordbookList.appendChild(card);
  });
}

async function saveWordbook(event) {
  event.preventDefault();

  const id = wordbookIdInput.value;
  const payload = {
    name: wordbookNameInput.value.trim(),
    description: wordbookDescriptionInput.value.trim() || null,
  };

  const isEditing = Boolean(id);
  const url = isEditing ? `${API.wordbooks}/${id}` : API.wordbooks;
  const method = isEditing ? "PATCH" : "POST";

  try {
    await requestJson(url, {
      method,
      body: JSON.stringify(payload),
    });

    clearWordbookForm();
    await loadWordbooks();
    await loadWords();

    setStatus(wordbookStatus, isEditing ? "單字本已更新" : "單字本已新增");
  } catch (error) {
    setStatus(wordbookStatus, error.message);
  }
}

async function handleWordbookListClick(event) {
  const button = event.target.closest("button");
  if (!button) return;

  const id = button.dataset.id;
  const action = button.dataset.action;

  if (action === "edit-wordbook") {
    const wordbook = wordbooks.find((item) => Number(item.id) === Number(id));
    if (!wordbook) return;

    wordbookIdInput.value = wordbook.id;
    wordbookNameInput.value = wordbook.name;
    wordbookDescriptionInput.value = wordbook.description || "";
    switchTab("wordbooks");
    wordbookNameInput.focus();
  }

  if (action === "delete-wordbook") {
    const confirmed = window.confirm("刪除單字本會一起刪除底下的單字，確定嗎？");
    if (!confirmed) return;

    try {
      await requestJson(`${API.wordbooks}/${id}`, { method: "DELETE" });
      await loadWordbooks();
      await loadWords();
      clearWordbookForm();
      setStatus(wordbookStatus, "單字本已刪除");
    } catch (error) {
      setStatus(wordbookStatus, error.message);
    }
  }
}

async function loadWords() {
  setStatus(wordStatus, "Loading...");

  try {
    const level = filterJlptSelect.value;
    const url = level ? `${API.words}?jlpt_level=${encodeURIComponent(level)}` : API.words;

    const data = await requestJson(url);
    words = data.items || [];

    renderWords();

    document.querySelector("#home-word-count").textContent = words.length;

    setStatus(wordStatus, `${words.length} 個單字`);
  } catch (error) {
    setStatus(wordStatus, error.message);
  }
}

function renderWords() {
  wordList.textContent = "";

  if (words.length === 0) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.textContent = "目前沒有單字。";
    wordList.appendChild(empty);
    return;
  }

  words.forEach((word) => {
    const card = document.createElement("article");
    card.className = "item-card word-card";

    card.innerHTML = `
      <div>
        <div class="word-line">
          <h3>${escapeHtml(word.word)}</h3>
          <span class="badge">${escapeHtml(word.jlpt_level)}</span>
          <span class="badge light">${escapeHtml(POS_LABELS[word.part_of_speech] || word.part_of_speech)}</span>
        </div>
        <p class="sub-text">${escapeHtml(word.hiragana || "平假名：無")}</p>
        <p>${escapeHtml(word.meaning_zh)}</p>
        <p class="sub-text">單字本：${escapeHtml(getWordbookName(word.wordbook_id))}</p>
      </div>
      <div class="item-actions">
        <button class="secondary-button" data-action="edit-word" data-id="${word.id}">編輯</button>
        <button class="danger-button" data-action="delete-word" data-id="${word.id}">刪除</button>
      </div>
    `;

    wordList.appendChild(card);
  });
}

async function saveWord(event) {
  event.preventDefault();

  if (!wordWordbookSelect.value) {
    setStatus(wordStatus, "請先建立單字本");
    return;
  }

  const id = wordIdInput.value;

  const payload = {
    wordbook_id: Number(wordWordbookSelect.value),
    word: wordTextInput.value.trim(),
    hiragana: wordHiraganaInput.value.trim() || null,
    jlpt_level: wordJlptSelect.value,
    part_of_speech: wordPartOfSpeechSelect.value,
    meaning_zh: wordMeaningInput.value.trim(),
  };

  const isEditing = Boolean(id);
  const url = isEditing ? `${API.words}/${id}` : API.words;
  const method = isEditing ? "PATCH" : "POST";

  try {
    await requestJson(url, {
      method,
      body: JSON.stringify(payload),
    });

    clearWordForm();
    await loadWords();

    setStatus(wordStatus, isEditing ? "單字已更新" : "單字已新增");
  } catch (error) {
    setStatus(wordStatus, error.message);
  }
}

async function handleWordListClick(event) {
  const button = event.target.closest("button");
  if (!button) return;

  const id = button.dataset.id;
  const action = button.dataset.action;

  if (action === "edit-word") {
    const word = words.find((item) => Number(item.id) === Number(id));
    if (!word) return;

    wordIdInput.value = word.id;
    wordWordbookSelect.value = word.wordbook_id;
    wordTextInput.value = word.word;
    wordHiraganaInput.value = word.hiragana || "";
    wordJlptSelect.value = word.jlpt_level;
    wordPartOfSpeechSelect.value = word.part_of_speech;
    wordMeaningInput.value = word.meaning_zh;

    switchTab("words");
    wordTextInput.focus();
  }

  if (action === "delete-word") {
    const confirmed = window.confirm("確定要刪除這個單字嗎？");
    if (!confirmed) return;

    try {
      await requestJson(`${API.words}/${id}`, { method: "DELETE" });
      await loadWords();
      clearWordForm();
      setStatus(wordStatus, "單字已刪除");
    } catch (error) {
      setStatus(wordStatus, error.message);
    }
  }
}

function getSelectedQuizLevels() {
  return Array.from(document.querySelectorAll('input[name="quiz-level"]:checked'))
    .map((input) => input.value);
}

function shuffleArray(array) {
  return [...array].sort(() => Math.random() - 0.5);
}

async function startQuiz() {
  const levels = getSelectedQuizLevels();

  if (levels.length === 0) {
    setStatus(quizStatus, "請至少選擇一個 JLPT 等級");
    return;
  }

  const query = levels.map((level) => `levels=${encodeURIComponent(level)}`).join("&");

  try {
    const data = await requestJson(`${API.quizWords}?${query}`);

    quizWords = shuffleArray(data.items || []);
    quizIndex = 0;
    quizShowingMeaning = false;

    if (quizWords.length === 0) {
      setStatus(quizStatus, "沒有符合條件的單字");
      return;
    }

    startQuizButton.disabled = true;
    endQuizButton.disabled = false;
    quizCard.classList.remove("hidden");

    renderQuizCard();
    setStatus(quizStatus, `測驗中：共 ${quizWords.length} 個單字`);
  } catch (error) {
    setStatus(quizStatus, error.message);
  }
}

function renderQuizCard() {
  const current = quizWords[quizIndex];

  if (!current) {
    endQuiz("測驗結束");
    return;
  }

  quizLevel.textContent = `${current.jlpt_level} · ${POS_LABELS[current.part_of_speech] || current.part_of_speech}`;
  quizWord.textContent = current.word;
  quizHiragana.textContent = current.hiragana || "";
  quizMeaning.textContent = current.meaning_zh;
  quizMeaning.classList.add("hidden");
  quizNextButton.textContent = "顯示中文意思";
  quizShowingMeaning = false;
}

function handleQuizNext() {
  if (quizWords.length === 0) return;

  if (!quizShowingMeaning) {
    quizMeaning.classList.remove("hidden");
    quizNextButton.textContent = "下一個單字";
    quizShowingMeaning = true;
    return;
  }

  quizIndex = (quizIndex + 1) % quizWords.length;
  renderQuizCard();
}

function endQuiz(message = "已結束測驗") {
  quizWords = [];
  quizIndex = 0;
  quizShowingMeaning = false;

  quizCard.classList.add("hidden");
  startQuizButton.disabled = false;
  endQuizButton.disabled = true;

  setStatus(quizStatus, message);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

tabButtons.forEach((button) => {
  button.addEventListener("click", () => switchTab(button.dataset.tab));
});

document.querySelectorAll(".nav-shortcut").forEach((button) => {
  button.addEventListener("click", () => {
    switchTab(button.dataset.target);
  });
});

wordbookForm.addEventListener("submit", saveWordbook);
clearWordbookButton.addEventListener("click", clearWordbookForm);
wordbookList.addEventListener("click", handleWordbookListClick);

wordForm.addEventListener("submit", saveWord);
clearWordButton.addEventListener("click", clearWordForm);
wordList.addEventListener("click", handleWordListClick);
filterJlptSelect.addEventListener("change", loadWords);

startQuizButton.addEventListener("click", startQuiz);
endQuizButton.addEventListener("click", () => endQuiz());
quizNextButton.addEventListener("click", handleQuizNext);

document.addEventListener("DOMContentLoaded", async () => {
  await loadWordbooks();
  await loadWords();
});