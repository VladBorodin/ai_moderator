const refreshLogsButton = document.getElementById("refreshLogsButton");
const logsEmptyState = document.getElementById("logsEmptyState");
const logsTableWrap = document.getElementById("logsTableWrap");
const logsTableBody = document.getElementById("logsTableBody");

refreshLogsButton.addEventListener("click", loadLogs);

document.addEventListener("DOMContentLoaded", loadLogs);

async function loadLogs() {
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

		renderLogs(logs);
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

		const verdictText = log.verdict === 1 ? "offensive" : "no_offensive";
		const verdictClass = log.verdict === 1 ? "badge danger" : "badge success";

		row.innerHTML = `
			<td>${escapeHtml(log.id)}</td>
			<td>${escapeHtml(formatDate(log.created_on))}</td>
			<td>${escapeHtml(log.source_system ?? "-")}</td>
			<td>${escapeHtml(log.chat_id ?? "-")}</td>
			<td>${escapeHtml(log.user_name ?? log.user_id ?? "-")}</td>
			<td class="description-cell">${escapeHtml(log.last_message_text ?? "-")}</td>
			<td><span class="${verdictClass}">${verdictText}</span></td>
			<td><span class="level-pill">${escapeHtml(log.offense_level ?? "-")}</span></td>
			<td class="description-cell">${escapeHtml(log.description ?? log.error_text ?? "-")}</td>
		`;

		logsTableBody.appendChild(row);
	}
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

function escapeHtml(value) {
	return String(value)
		.replaceAll("&", "&amp;")
		.replaceAll("<", "&lt;")
		.replaceAll(">", "&gt;")
		.replaceAll('"', "&quot;")
		.replaceAll("'", "&#039;");
}