const refreshSystemSettingsButton = document.getElementById("refreshSystemSettingsButton");
const systemSettingsEmptyState = document.getElementById("systemSettingsEmptyState");
const systemSettingsList = document.getElementById("systemSettingsList");

refreshSystemSettingsButton.addEventListener("click", loadSystemSettings);
document.addEventListener("DOMContentLoaded", loadSystemSettings);

async function loadSystemSettings() {
	try {
		const response = await fetch("/settings/system-settings");
		const settings = await response.json();

		if (!response.ok || !Array.isArray(settings) || settings.length === 0) {
			showEmptyState();
			return;
		}

		renderSystemSettings(settings);
	} catch (error) {
		showEmptyState();
	}
}

function renderSystemSettings(settings) {
	systemSettingsEmptyState.classList.add("hidden");
	systemSettingsList.classList.remove("hidden");
	systemSettingsList.innerHTML = "";

	for (const setting of settings) {
		const card = document.createElement("div");
		card.className = "setting-card";

		card.innerHTML = `
			<div class="setting-card-header">
				<div>
					<div class="setting-code">${escapeHtml(setting.code)}</div>
					<div class="setting-description">${escapeHtml(setting.description ?? "-")}</div>
				</div>
			</div>

			<div class="setting-edit-row">
				<div class="form-row">
					<label>Значение</label>
					<input class="setting-value-input" type="text" value="${escapeAttribute(setting.value ?? "")}">
				</div>

				<div class="form-row">
                    <label>Описание</label>
                    <textarea class="setting-description-input" rows="3">${escapeHtml(setting.description ?? "")}</textarea>
                </div>

				<div class="setting-actions">
					<button class="primary-button" type="button">Сохранить</button>
				</div>
			</div>

			<div class="setting-message hidden"></div>
		`;

		const valueInput = card.querySelector(".setting-value-input");
		const descriptionInput = card.querySelector(".setting-description-input");
		const saveButton = card.querySelector(".primary-button");
		const message = card.querySelector(".setting-message");

		saveButton.addEventListener("click", async () => {
			await saveSystemSetting(
				setting.code,
				valueInput.value,
				descriptionInput.value,
				message
			);
		});

		systemSettingsList.appendChild(card);
	}
}

async function saveSystemSetting(code, value, description, messageElement) {
	clearMessage(messageElement);

	try {
		const response = await fetch(`/settings/system-settings/${encodeURIComponent(code)}`, {
			method: "PUT",
			headers: {
				"Content-Type": "application/json"
			},
			body: JSON.stringify({
				value: value,
				description: description
			})
		});

		const responseBody = await response.json();

		if (!response.ok) {
			showMessage(messageElement, `Ошибка сохранения: ${JSON.stringify(responseBody)}`, true);
			return;
		}

		showMessage(messageElement, "Настройка сохранена.", false);
	} catch (error) {
		showMessage(messageElement, `Ошибка запроса: ${error}`, true);
	}
}

function showEmptyState() {
	systemSettingsEmptyState.classList.remove("hidden");
	systemSettingsList.classList.add("hidden");
	systemSettingsList.innerHTML = "";
}

function showMessage(element, text, isError) {
	element.classList.remove("hidden");
	element.className = isError ? "setting-message error" : "setting-message success";
	element.textContent = text;
}

function clearMessage(element) {
	element.classList.add("hidden");
	element.textContent = "";
}

function escapeHtml(value) {
	return String(value)
		.replaceAll("&", "&amp;")
		.replaceAll("<", "&lt;")
		.replaceAll(">", "&gt;")
		.replaceAll('"', "&quot;")
		.replaceAll("'", "&#039;");
}

function escapeAttribute(value) {
	return escapeHtml(value);
}