const refreshLogsButton = document.getElementById("refreshLogsButton");
const logsEmptyState = document.getElementById("logsEmptyState");
const logsTableWrap = document.getElementById("logsTableWrap");
const logsTableBody = document.getElementById("logsTableBody");

const autoRefreshLogsCheckbox = document.getElementById("autoRefreshLogsCheckbox");
const logsRefreshText = document.getElementById("logsRefreshText");
const newLogsBadge = document.getElementById("newLogsBadge");

let refreshIntervalSeconds = 15;
let secondsUntilRefresh = refreshIntervalSeconds;
let currentFirstLogId = null;
let hasOpenDetails = false;

refreshLogsButton.addEventListener("click", loadLogs);

document.addEventListener("DOMContentLoaded", loadLogs);

async function loadLogs(forceRender) {
	try {
		const response = await fetch("/moderation/logs?limit=50&offset=0");
		const logs = await response.json();

		if (!response.ok) {
			showEmptyLogs();
			return;
		}

		if (!Array.isArray(logs) || logs.length === 0) {
			showEmptyLogs();
			return;
		}

		const firstLogId = logs[0]?.id ?? null;

		if (!forceRender && hasOpenDetails && firstLogId !== currentFirstLogId) {
			showNewLogsBadge();
			return;
		}

		currentFirstLogId = firstLogId;
		hideNewLogsBadge();
		renderLogs(logs);
		
		hasOpenDetails = false;
		secondsUntilRefresh = refreshIntervalSeconds;
		logsRefreshText.textContent = `Автообновление через ${refreshIntervalSeconds} сек.`;
	} catch (error) {
		showEmptyLogs();
	}
}

function renderLogs(logs) {
	logsEmptyState.classList.add("hidden");
	logsTableWrap.classList.remove("hidden");
	logsTableBody.innerHTML = "";

	for (const log of logs) {
		const row = document.createElement("tr");

		let verdictText = "failed";
		let verdictClass = "badge warning";

		if (log.error_text) {
			verdictText = "failed";
			verdictClass = "badge warning";
		} else if (log.verdict === 1) {
			verdictText = "offensive";
			verdictClass = "badge danger";
		} else if (log.verdict === 0) {
			verdictText = "no_offensive";
			verdictClass = "badge success";
		}

		const detailsRowId = `details-${log.id}`;

		row.innerHTML = `
			<td>${escapeHtml(formatDate(log.created_on))}</td>
			<td>${escapeHtml(log.source_system ?? "-")}</td>
			<td>${escapeHtml(log.chat_id ?? "-")}</td>
			<td>${escapeHtml(log.user_name ?? log.user_id ?? "-")}</td>
			<td class="description-cell">${escapeHtml(log.last_message_text ?? "-")}</td>
			<td><span class="${verdictClass}">${verdictText}</span></td>
			<td><span class="level-pill">${escapeHtml(log.offense_level ?? "-")}</span></td>
			<td>${escapeHtml(formatProcessingTime(log.processing_time_ms))}</td>
			<td class="description-cell">${escapeHtml(log.description ?? log.error_text ?? "-")}</td>
			<td>
				<button class="table-action-button" type="button" data-details-id="${detailsRowId}">
					Детали
				</button>
			</td>
		`;

		const detailsRow = document.createElement("tr");
		detailsRow.id = detailsRowId;
		detailsRow.className = "details-row hidden";

		detailsRow.innerHTML = `
			<td colspan="10">
				<div class="details-panel">
					<div class="details-grid">
						<div class="details-meta-card">
							<div class="result-label">Log ID</div>
							<div class="details-value">${escapeHtml(log.id)}</div>
						</div>

						<div class="details-meta-card">
							<div class="result-label">External message ID</div>
							<div class="details-value">${escapeHtml(log.external_message_id ?? "-")}</div>
						</div>

						<div class="details-meta-card">
							<div class="result-label">Processing time</div>
							<div class="details-value">${escapeHtml(formatProcessingTime(log.processing_time_ms))}</div>
						</div>

						<div class="details-meta-card">
							<div class="result-label">Error text</div>
							<div class="details-value ${log.error_text ? "danger-text" : ""}">${escapeHtml(log.error_text ?? "-")}</div>
						</div>
					</div>

					<div class="details-json-grid">
						<div class="json-box">
							<div class="result-label">Request JSON</div>
							<pre>${escapeHtml(JSON.stringify(log.request_json, null, 2))}</pre>
						</div>

						<div class="json-box">
							<div class="result-label">Response JSON</div>
							<pre>${escapeHtml(formatNullableJson(log.response_json))}</pre>
						</div>
					</div>
				</div>
			</td>
		`;

		logsTableBody.appendChild(row);
		logsTableBody.appendChild(detailsRow);

		const detailsButton = row.querySelector("[data-details-id]");

		detailsButton.addEventListener("click", () => {
			toggleDetails(detailsRowId, detailsButton);
		});
	}
}

function toggleDetails(detailsRowId, button) {
	const detailsRow = document.getElementById(detailsRowId);

	if (!detailsRow) {
		return;
	}

	const isHidden = detailsRow.classList.contains("hidden");

	if (isHidden) {
		detailsRow.classList.remove("hidden");
		button.textContent = "Скрыть";
	} else {
		detailsRow.classList.add("hidden");
		button.textContent = "Детали";
	}

	hasOpenDetails = Boolean(document.querySelector(".details-row:not(.hidden)"));
}

function showEmptyLogs() {
	logsEmptyState.classList.remove("hidden");
	logsTableWrap.classList.add("hidden");
	logsTableBody.innerHTML = "";
}

function formatDate(value) {
	if (!value) {
		return "-";
	}

	const date = new Date(value);

	if (Number.isNaN(date.getTime())) {
		return value;
	}

	return date.toLocaleString();
}

function formatProcessingTime(value) {
	if (value === null || value === undefined) {
		return "-";
	}

	return `${value} ms`;
}

function formatNullableJson(value) {
	if (value === null || value === undefined) {
		return "-";
	}

	return JSON.stringify(value, null, 2);
}

function escapeHtml(value) {
	return String(value)
		.replaceAll("&", "&amp;")
		.replaceAll("<", "&lt;")
		.replaceAll(">", "&gt;")
		.replaceAll('"', "&quot;")
		.replaceAll("'", "&#039;");
}

refreshLogsButton.addEventListener("click", async () => {
	hasOpenDetails = false;
	await loadLogs(true);
});

document.addEventListener("DOMContentLoaded", async () => {
	await loadLogs(true);
	startLogsRefreshTimer();
});

function startLogsRefreshTimer() {
	setInterval(async () => {
		if (!autoRefreshLogsCheckbox.checked) {
			logsRefreshText.textContent = "Автообновление выключено.";
			await checkForNewLogs();
			return;
		}

		if (hasOpenDetails) {
			logsRefreshText.textContent = "Автообновление на паузе: открыты детали.";
			await checkForNewLogs();
			return;
		}

		secondsUntilRefresh -= 1;

		if (secondsUntilRefresh <= 0) {
			await loadLogs(false);
			secondsUntilRefresh = refreshIntervalSeconds;
			return;
		}

		logsRefreshText.textContent = `Автообновление через ${secondsUntilRefresh} сек.`;
	}, 1000);
}

async function checkForNewLogs() {
	try {
		const response = await fetch("/moderation/logs?limit=1&offset=0");
		const logs = await response.json();

		if (!response.ok || !Array.isArray(logs) || logs.length === 0) {
			return;
		}

		const firstLogId = logs[0]?.id ?? null;

		if (currentFirstLogId && firstLogId && firstLogId !== currentFirstLogId) {
			showNewLogsBadge();
		}
	} catch {
		// Не шумим: это фоновая проверка.
	}
}

function showNewLogsBadge() {
	newLogsBadge.classList.remove("hidden");
}

function hideNewLogsBadge() {
	newLogsBadge.classList.add("hidden");
}

autoRefreshLogsCheckbox.addEventListener("change", async () => {
	secondsUntilRefresh = refreshIntervalSeconds;

	if (autoRefreshLogsCheckbox.checked) {
		logsRefreshText.textContent = `Автообновление через ${refreshIntervalSeconds} сек.`;

		if (!hasOpenDetails) {
			await loadLogs(false);
		}

		return;
	}

	logsRefreshText.textContent = "Автообновление выключено.";
	await checkForNewLogs();
});