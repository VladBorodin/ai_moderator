const healthModalButton = document.getElementById("healthModalButton");
const healthModalOverlay = document.getElementById("healthModalOverlay");
const closeHealthModalButton = document.getElementById("closeHealthModalButton");
const confirmHealthModalButton = document.getElementById("confirmHealthModalButton");
const refreshHealthModalButton = document.getElementById("refreshHealthModalButton");
const healthModalStatus = document.getElementById("healthModalStatus");
const healthModalJson = document.getElementById("healthModalJson");

if (healthModalButton) {
	healthModalButton.addEventListener("click", async () => {
		openHealthModal();
		await loadHealthStatus();
	});
}

if (closeHealthModalButton) {
	closeHealthModalButton.addEventListener("click", closeHealthModal);
}

if (confirmHealthModalButton) {
	confirmHealthModalButton.addEventListener("click", closeHealthModal);
}

if (refreshHealthModalButton) {
	refreshHealthModalButton.addEventListener("click", loadHealthStatus);
}

if (healthModalOverlay) {
	healthModalOverlay.addEventListener("click", (event) => {
		if (event.target === healthModalOverlay) {
			closeHealthModal();
		}
	});
}

document.addEventListener("keydown", (event) => {
	if (event.key === "Escape") {
		closeHealthModal();
	}
});

function openHealthModal() {
	healthModalOverlay.classList.remove("hidden");
}

function closeHealthModal() {
	healthModalOverlay.classList.add("hidden");
}

async function loadHealthStatus() {
	renderHealthLoading();

	try {
		const response = await fetch("/health");
		const responseBody = await response.json();

		healthModalJson.textContent = JSON.stringify(responseBody, null, 2);

		if (!response.ok) {
			renderHealthError(`Health вернул HTTP ${response.status}.`);
			return;
		}

		renderHealthSuccess("Сервис доступен.", "Endpoint /health успешно ответил.");
	} catch (error) {
		healthModalJson.textContent = String(error);
		renderHealthError("Не удалось выполнить запрос к /health.");
	}
}

function renderHealthLoading() {
	healthModalStatus.className = "health-status-card";
	healthModalStatus.innerHTML = `
		<div class="health-status-dot loading"></div>
		<div>
			<strong>Проверяем...</strong>
			<span>Выполняется запрос к /health.</span>
		</div>
	`;
	healthModalJson.textContent = "-";
}

function renderHealthSuccess(title, description) {
	healthModalStatus.className = "health-status-card success";
	healthModalStatus.innerHTML = `
		<div class="health-status-dot"></div>
		<div>
			<strong>${escapeHtml(title)}</strong>
			<span>${escapeHtml(description)}</span>
		</div>
	`;
}

function renderHealthError(description) {
	healthModalStatus.className = "health-status-card danger";
	healthModalStatus.innerHTML = `
		<div class="health-status-dot"></div>
		<div>
			<strong>Есть проблема</strong>
			<span>${escapeHtml(description)}</span>
		</div>
	`;
}

function escapeHtml(value) {
	return String(value)
		.replaceAll("&", "&amp;")
		.replaceAll("<", "&lt;")
		.replaceAll(">", "&gt;")
		.replaceAll('"', "&quot;")
		.replaceAll("'", "&#039;");
}