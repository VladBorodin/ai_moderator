const refreshPromptsButton = document.getElementById("refreshPromptsButton");
const promptsEmptyState = document.getElementById("promptsEmptyState");
const promptsList = document.getElementById("promptsList");

const activePromptCard = document.getElementById("activePromptCard");
const activePromptName = document.getElementById("activePromptName");
const activePromptMeta = document.getElementById("activePromptMeta");

const promptForm = document.getElementById("promptForm");
const promptId = document.getElementById("promptId");
const promptCode = document.getElementById("promptCode");
const promptName = document.getElementById("promptName");
const promptVersion = document.getElementById("promptVersion");
const promptIsActive = document.getElementById("promptIsActive");
const promptText = document.getElementById("promptText");
const resetPromptFormButton = document.getElementById("resetPromptFormButton");
const promptFormMessage = document.getElementById("promptFormMessage");
const promptFormTitle = document.getElementById("promptFormTitle");

const defaultPromptText = promptText.value;

refreshPromptsButton.addEventListener("click", loadPrompts);
resetPromptFormButton.addEventListener("click", resetPromptForm);
promptForm.addEventListener("submit", savePrompt);

document.addEventListener("DOMContentLoaded", loadPrompts);

async function loadPrompts() {
	clearPromptFormMessage();

	try {
		const response = await fetch("/settings/prompt-templates");
		const prompts = await response.json();

		if (!response.ok || !Array.isArray(prompts)) {
			showPromptsEmptyState();
			return;
		}

		renderPrompts(prompts);
		renderActivePrompt(prompts);
	} catch (error) {
		showPromptsEmptyState();
	}
}

function renderPrompts(prompts) {
	promptsList.innerHTML = "";

	if (prompts.length === 0) {
		showPromptsEmptyState();
		return;
	}

	promptsEmptyState.classList.add("hidden");
	promptsList.classList.remove("hidden");

	for (const prompt of prompts) {
		const card = document.createElement("div");
		card.className = prompt.is_active ? "provider-card active" : "provider-card";

		card.innerHTML = `
			<div class="provider-card-header">
				<div>
					<div class="provider-name">${escapeHtml(prompt.name)}</div>
					<div class="provider-url">${escapeHtml(prompt.code)}</div>
				</div>
				${prompt.is_active ? `<span class="badge success">active</span>` : `<span class="badge">inactive</span>`}
			</div>

			<div class="provider-meta-grid">
				<div>
					<span>Code</span>
					<strong>${escapeHtml(prompt.code)}</strong>
				</div>
				<div>
					<span>Version</span>
					<strong>${escapeHtml(prompt.version)}</strong>
				</div>
				<div>
					<span>Length</span>
					<strong>${escapeHtml(prompt.prompt_text.length)} chars</strong>
				</div>
			</div>

			<div class="prompt-preview">${escapeHtml(cutText(prompt.prompt_text, 360))}</div>

			<div class="provider-actions">
				<button class="secondary-button" type="button" data-action="edit" data-prompt-id="${prompt.id}">Редактировать</button>
				<button class="secondary-button" type="button" data-action="activate" data-prompt-id="${prompt.id}" ${prompt.is_active ? "disabled" : ""}>Сделать активным</button>
				<button class="danger-button" type="button" data-action="delete" data-prompt-id="${prompt.id}" ${prompt.is_active ? "disabled" : ""}>Удалить</button>
			</div>
		`;

		card.querySelector('[data-action="edit"]').addEventListener("click", () => {
			fillPromptForm(prompt);
		});

		const activateButton = card.querySelector('[data-action="activate"]');

		if (activateButton) {
			activateButton.addEventListener("click", () => {
				activatePrompt(prompt.id);
			});
		}

		const deleteButton = card.querySelector('[data-action="delete"]');

		if (deleteButton) {
			deleteButton.addEventListener("click", () => {
				deletePrompt(prompt.id, prompt.name);
			});
		}

		promptsList.appendChild(card);
	}
}

function renderActivePrompt(prompts) {
	const activePrompt = prompts.find(prompt => prompt.is_active);

	if (!activePrompt) {
		activePromptCard.classList.add("hidden");
		return;
	}

	activePromptCard.classList.remove("hidden");
	activePromptName.textContent = activePrompt.name;
	activePromptMeta.textContent = `${activePrompt.code} · version ${activePrompt.version} · ${activePrompt.prompt_text.length} chars`;
}

function showPromptsEmptyState() {
	promptsEmptyState.classList.remove("hidden");
	promptsList.classList.add("hidden");
	activePromptCard.classList.add("hidden");
	promptsList.innerHTML = "";
}

async function savePrompt(event) {
	event.preventDefault();
	clearPromptFormMessage();

	const dto = {
		code: promptCode.value,
		name: promptName.value,
		prompt_text: promptText.value,
		version: Number(promptVersion.value),
		is_active: promptIsActive.checked
	};

	const currentPromptId = promptId.value;
	const url = currentPromptId
		? `/settings/prompt-templates/${currentPromptId}`
		: "/settings/prompt-templates";

	const method = currentPromptId ? "PUT" : "POST";

	try {
		const response = await fetch(url, {
			method: method,
			headers: {
				"Content-Type": "application/json"
			},
			body: JSON.stringify(dto)
		});

		const responseBody = await response.json();

		if (!response.ok) {
			showPromptFormMessage(`Ошибка сохранения: ${JSON.stringify(responseBody)}`, true);
			return;
		}

		showPromptFormMessage("Промт сохранен.", false);
		resetPromptForm();
		await loadPrompts();
	} catch (error) {
		showPromptFormMessage(`Ошибка запроса: ${error}`, true);
	}
}

async function activatePrompt(id) {
	clearPromptFormMessage();

	try {
		const response = await fetch(`/settings/prompt-templates/${id}/activate`, {
			method: "POST"
		});

		if (!response.ok) {
			const responseBody = await response.json();
			showPromptFormMessage(`Ошибка активации: ${JSON.stringify(responseBody)}`, true);
			return;
		}

		showPromptFormMessage("Промт активирован.", false);
		await loadPrompts();
	} catch (error) {
		showPromptFormMessage(`Ошибка запроса: ${error}`, true);
	}
}

async function deletePrompt(id, name) {
	clearPromptFormMessage();

	const isConfirmed = confirm(`Удалить промт "${name}"? Активный промт удалить нельзя.`);

	if (!isConfirmed) {
		return;
	}

	try {
		const response = await fetch(`/settings/prompt-templates/${id}`, {
			method: "DELETE"
		});

		if (!response.ok) {
			const responseBody = await response.json();
			showPromptFormMessage(`Ошибка удаления: ${JSON.stringify(responseBody)}`, true);
			return;
		}

		showPromptFormMessage("Промт удален.", false);
		resetPromptForm();
		await loadPrompts();
	} catch (error) {
		showPromptFormMessage(`Ошибка запроса: ${error}`, true);
	}
}

function fillPromptForm(prompt) {
	promptFormTitle.textContent = "Редактирование промта";
	promptId.value = prompt.id;
	promptCode.value = prompt.code;
	promptName.value = prompt.name;
	promptText.value = prompt.prompt_text;
	promptVersion.value = prompt.version;
	promptIsActive.checked = prompt.is_active;
	clearPromptFormMessage();
}

function resetPromptForm() {
	promptFormTitle.textContent = "Новый промт";
	promptId.value = "";
	promptCode.value = "default_moderation_prompt";
	promptName.value = "Базовый промт модерации";
	promptText.value = defaultPromptText;
	promptVersion.value = "1";
	promptIsActive.checked = true;
	clearPromptFormMessage();
}

function showPromptFormMessage(message, isError) {
	promptFormMessage.classList.remove("hidden");
	promptFormMessage.className = isError ? "form-message error" : "form-message success";
	promptFormMessage.textContent = message;
}

function clearPromptFormMessage() {
	promptFormMessage.classList.add("hidden");
	promptFormMessage.textContent = "";
}

function cutText(value, maxLength) {
	if (!value) {
		return "";
	}

	if (value.length <= maxLength) {
		return value;
	}

	return `${value.slice(0, maxLength)}...`;
}

function escapeHtml(value) {
	return String(value)
		.replaceAll("&", "&amp;")
		.replaceAll("<", "&lt;")
		.replaceAll(">", "&gt;")
		.replaceAll('"', "&quot;")
		.replaceAll("'", "&#039;");
}