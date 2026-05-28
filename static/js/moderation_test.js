const defaultMessagesJson = `[
	{
		"role": "user",
		"name": "Петр",
		"text": "И мне выпал тот самый билет, и я победил!"
	},
	{
		"role": "user",
		"name": "Сергей",
		"text": "Ну ты удачливый сукин сын!"
	}
]`;

const moderationForm = document.getElementById("moderationForm");
const resetExampleButton = document.getElementById("resetExampleButton");

const resultEmptyState = document.getElementById("resultEmptyState");
const resultPanel = document.getElementById("resultPanel");
const resultVerdict = document.getElementById("resultVerdict");
const resultLevel = document.getElementById("resultLevel");
const resultDescription = document.getElementById("resultDescription");
const resultJson = document.getElementById("resultJson");

resetExampleButton.addEventListener("click", () => {
	document.getElementById("chatId").value = "test_chat";
	document.getElementById("userId").value = "user_1";
	document.getElementById("triggerWord").value = "сукин сын";
	document.getElementById("messagesJson").value = defaultMessagesJson;
});

moderationForm.addEventListener("submit", async (event) => {
	event.preventDefault();

	clearResultState();

	let messages;

	try {
		messages = JSON.parse(document.getElementById("messagesJson").value);
	} catch (error) {
		showErrorResult("Некорректный JSON в поле Messages JSON.");
		return;
	}

	const requestBody = {
		chat_id: document.getElementById("chatId").value || null,
		user_id: document.getElementById("userId").value || null,
		trigger_word: document.getElementById("triggerWord").value || null,
		messages: messages
	};

	try {
		const response = await fetch("/moderation/check", {
			method: "POST",
			headers: {
				"Content-Type": "application/json"
			},
			body: JSON.stringify(requestBody)
		});

		const responseBody = await response.json();

		if (!response.ok) {
			showErrorResult(JSON.stringify(responseBody, null, 2));
			return;
		}

		showSuccessResult(responseBody);
	} catch (error) {
		showErrorResult(`Ошибка запроса: ${error}`);
	}
});

function clearResultState() {
	resultEmptyState.classList.add("hidden");
	resultPanel.classList.remove("hidden");
	resultVerdict.className = "badge";
	resultVerdict.textContent = "-";
	resultLevel.textContent = "-";
	resultDescription.textContent = "";
	resultJson.textContent = "";
}

function showSuccessResult(responseBody) {
	const result = responseBody.result;
	const isOffensive = result.verdict === 1;

	resultVerdict.textContent = isOffensive ? "offensive" : "no_offensive";
	resultVerdict.className = isOffensive ? "badge danger" : "badge success";

	resultLevel.textContent = result.offense_level;
	resultDescription.textContent = result.description;
	resultJson.textContent = JSON.stringify(responseBody, null, 2);
}

function showErrorResult(message) {
	resultEmptyState.classList.add("hidden");
	resultPanel.classList.remove("hidden");

	resultVerdict.textContent = "error";
	resultVerdict.className = "badge danger";
	resultLevel.textContent = "-";
	resultDescription.textContent = message;
	resultJson.textContent = message;
}