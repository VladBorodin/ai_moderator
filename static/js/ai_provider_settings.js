const refreshProvidersButton = document.getElementById("refreshProvidersButton");
const providersEmptyState = document.getElementById("providersEmptyState");
const providersList = document.getElementById("providersList");

const activeProviderCard = document.getElementById("activeProviderCard");
const activeProviderName = document.getElementById("activeProviderName");
const activeProviderMeta = document.getElementById("activeProviderMeta");

const aiProviderForm = document.getElementById("aiProviderForm");
const providerId = document.getElementById("providerId");
const providerName = document.getElementById("providerName");
const providerType = document.getElementById("providerType");
const providerUrl = document.getElementById("providerUrl");
const modelName = document.getElementById("modelName");
const apiKey = document.getElementById("apiKey");
const timeoutSeconds = document.getElementById("timeoutSeconds");
const isActive = document.getElementById("isActive");
const resetProviderFormButton = document.getElementById("resetProviderFormButton");
const providerFormMessage = document.getElementById("providerFormMessage");
const formTitle = document.getElementById("formTitle");

refreshProvidersButton.addEventListener("click", loadProviders);
resetProviderFormButton.addEventListener("click", resetProviderForm);
aiProviderForm.addEventListener("submit", saveProvider);

document.addEventListener("DOMContentLoaded", loadProviders);

async function loadProviders() {
	clearFormMessage();

	try {
		const response = await fetch("/settings/ai-providers");
		const providers = await response.json();

		if (!response.ok || !Array.isArray(providers)) {
			showProvidersEmptyState();
			return;
		}

		renderProviders(providers);
		renderActiveProvider(providers);
	} catch (error) {
		showProvidersEmptyState();
	}
}

function renderProviders(providers) {
	providersList.innerHTML = "";

	if (providers.length === 0) {
		showProvidersEmptyState();
		return;
	}

	providersEmptyState.classList.add("hidden");
	providersList.classList.remove("hidden");

	for (const provider of providers) {
		const card = document.createElement("div");
		card.className = provider.is_active ? "provider-card active" : "provider-card";

		card.innerHTML = `
			<div class="provider-card-header">
				<div>
					<div class="provider-name">${escapeHtml(provider.name)}</div>
					<div class="provider-url">${escapeHtml(provider.provider_url)}</div>
				</div>
				${provider.is_active ? `<span class="badge success">active</span>` : `<span class="badge">inactive</span>`}
			</div>

			<div class="provider-meta-grid">
				<div>
					<span>Type</span>
					<strong>${escapeHtml(provider.provider_type)}</strong>
				</div>
				<div>
					<span>Model</span>
					<strong>${escapeHtml(provider.model_name)}</strong>
				</div>
				<div>
					<span>Timeout</span>
					<strong>${escapeHtml(provider.timeout_seconds)} sec</strong>
				</div>
			</div>

			<div class="provider-actions">
                <button class="secondary-button" type="button" data-action="edit" data-provider-id="${provider.id}">Редактировать</button>
                <button class="secondary-button" type="button" data-action="activate" data-provider-id="${provider.id}" ${provider.is_active ? "disabled" : ""}>Сделать активным</button>
                <button class="danger-button" type="button" data-action="delete" data-provider-id="${provider.id}" ${provider.is_active ? "disabled" : ""}>Удалить</button>
            </div>
		`;

		card.querySelector('[data-action="edit"]').addEventListener("click", () => {
			fillProviderForm(provider);
		});

		const activateButton = card.querySelector('[data-action="activate"]');

		if (activateButton) {
			activateButton.addEventListener("click", () => {
				activateProvider(provider.id);
			});
		}

        const deleteButton = card.querySelector('[data-action="delete"]');

        if (deleteButton) {
            deleteButton.addEventListener("click", () => {
                deleteProvider(provider.id, provider.name);
            });
        }

		providersList.appendChild(card);
	}
}

function renderActiveProvider(providers) {
	const activeProvider = providers.find(provider => provider.is_active);

	if (!activeProvider) {
		activeProviderCard.classList.add("hidden");
		return;
	}

	activeProviderCard.classList.remove("hidden");
	activeProviderName.textContent = activeProvider.name;
	activeProviderMeta.textContent = `${activeProvider.provider_type} · ${activeProvider.model_name} · ${activeProvider.provider_url}`;
}

function showProvidersEmptyState() {
	providersEmptyState.classList.remove("hidden");
	providersList.classList.add("hidden");
	activeProviderCard.classList.add("hidden");
	providersList.innerHTML = "";
}

async function saveProvider(event) {
	event.preventDefault();
	clearFormMessage();

	const dto = {
		name: providerName.value,
		provider_type: providerType.value,
		provider_url: providerUrl.value,
		model_name: modelName.value,
		api_key: apiKey.value || "",
		timeout_seconds: Number(timeoutSeconds.value),
		is_active: isActive.checked
	};

	const currentProviderId = providerId.value;
	const url = currentProviderId
		? `/settings/ai-providers/${currentProviderId}`
		: "/settings/ai-providers";

	const method = currentProviderId ? "PUT" : "POST";

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
			showFormMessage(`Ошибка сохранения: ${JSON.stringify(responseBody)}`, true);
			return;
		}

		showFormMessage("Провайдер сохранен.", false);
		resetProviderForm();
		await loadProviders();
	} catch (error) {
		showFormMessage(`Ошибка запроса: ${error}`, true);
	}
}

async function activateProvider(id) {
	clearFormMessage();

	try {
		const response = await fetch(`/settings/ai-providers/${id}/activate`, {
			method: "POST"
		});

		if (!response.ok) {
			const responseBody = await response.json();
			showFormMessage(`Ошибка активации: ${JSON.stringify(responseBody)}`, true);
			return;
		}

		showFormMessage("Провайдер активирован.", false);
		await loadProviders();
	} catch (error) {
		showFormMessage(`Ошибка запроса: ${error}`, true);
	}
}

function fillProviderForm(provider) {
	formTitle.textContent = "Редактирование провайдера";
	providerId.value = provider.id;
	providerName.value = provider.name;
	providerType.value = provider.provider_type;
	providerUrl.value = provider.provider_url;
	modelName.value = provider.model_name;
	apiKey.value = provider.api_key || "";
	timeoutSeconds.value = provider.timeout_seconds;
	isActive.checked = provider.is_active;
	clearFormMessage();
}

function resetProviderForm() {
	formTitle.textContent = "Новый провайдер";
	providerId.value = "";
	providerName.value = "Local Ollama";
	providerType.value = "openai_compatible";
	providerUrl.value = "http://localhost:11434/v1/chat/completions";
	modelName.value = "llama3.1";
	apiKey.value = "";
	timeoutSeconds.value = "60";
	isActive.checked = true;
	clearFormMessage();
}

function showFormMessage(message, isError) {
	providerFormMessage.classList.remove("hidden");
	providerFormMessage.className = isError ? "form-message error" : "form-message success";
	providerFormMessage.textContent = message;
}

function clearFormMessage() {
	providerFormMessage.classList.add("hidden");
	providerFormMessage.textContent = "";
}

function escapeHtml(value) {
	return String(value)
		.replaceAll("&", "&amp;")
		.replaceAll("<", "&lt;")
		.replaceAll(">", "&gt;")
		.replaceAll('"', "&quot;")
		.replaceAll("'", "&#039;");
}

async function deleteProvider(id, name) {
	clearFormMessage();

	try {
		const response = await fetch(`/settings/ai-providers/${id}`, {
			method: "DELETE"
		});

		if (!response.ok) {
			const responseBody = await response.json();
			showFormMessage(`Ошибка удаления: ${JSON.stringify(responseBody)}`, true);
			return;
		}

		showFormMessage("Провайдер удален.", false);
		resetProviderForm();
		await loadProviders();
	} catch (error) {
		showFormMessage(`Ошибка запроса: ${error}`, true);
	}
}