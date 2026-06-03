const refreshSystemLogsButton = document.getElementById("refreshSystemLogsButton");
const linesCount = document.getElementById("linesCount");

const appLogContent = document.getElementById("appLogContent");
const errorLogContent = document.getElementById("errorLogContent");

const appLogLinesCount = document.getElementById("appLogLinesCount");
const errorLogLinesCount = document.getElementById("errorLogLinesCount");

refreshSystemLogsButton.addEventListener("click", loadSystemLogs);
document.addEventListener("DOMContentLoaded", loadSystemLogs);

async function loadSystemLogs() {
	const lines = Number(linesCount.value || 200);

	try {
		const response = await fetch(`/api/system-logs?lines=${lines}`);
		const responseBody = await response.json();

		if (!response.ok) {
			showLogError(responseBody);
			return;
		}

		renderLogs(responseBody);
	} catch (error) {
		showLogError(error);
	}
}

function renderLogs(logs) {
	const appLogLines = logs.app_log || [];
	const errorLogLines = logs.error_log || [];

	appLogContent.textContent = appLogLines.join("\n") || "app.log пуст или еще не создан.";
	errorLogContent.textContent = errorLogLines.join("\n") || "error.log пуст или еще не создан.";

	appLogLinesCount.textContent = `${appLogLines.length} lines`;
	errorLogLinesCount.textContent = `${errorLogLines.length} lines`;
}

function showLogError(error) {
	const errorText = error instanceof Error
		? error.message
		: JSON.stringify(error, null, 2);

	appLogContent.textContent = `Ошибка загрузки логов: ${errorText}`;
	errorLogContent.textContent = "";
	appLogLinesCount.textContent = "error";
	errorLogLinesCount.textContent = "error";
}