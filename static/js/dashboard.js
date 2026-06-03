const totalChecksMetric = document.getElementById("totalChecksMetric");
const offensiveChecksMetric = document.getElementById("offensiveChecksMetric");
const nonOffensiveChecksMetric = document.getElementById("nonOffensiveChecksMetric");
const failedChecksMetric = document.getElementById("failedChecksMetric");
const averageProcessingTimeMetric = document.getElementById("averageProcessingTimeMetric");

const activeProviderStatus = document.getElementById("activeProviderStatus");
const activePromptStatus = document.getElementById("activePromptStatus");

const verdictDistributionChart = document.getElementById("verdictDistributionChart");
const offenseLevelChart = document.getElementById("offenseLevelChart");
const checksByDayChart = document.getElementById("checksByDayChart");

const refreshDashboardButton = document.getElementById("refreshDashboardButton");

const dashboardWarnings = document.getElementById("dashboardWarnings");

const dayStatisticsModalOverlay = document.getElementById("dayStatisticsModalOverlay");
const closeDayStatisticsModalButton = document.getElementById("closeDayStatisticsModalButton");
const confirmDayStatisticsModalButton = document.getElementById("confirmDayStatisticsModalButton");

const dayStatisticsTitle = document.getElementById("dayStatisticsTitle");
const dayTotalChecks = document.getElementById("dayTotalChecks");
const dayOffensiveChecks = document.getElementById("dayOffensiveChecks");
const dayNonOffensiveChecks = document.getElementById("dayNonOffensiveChecks");
const dayFailedChecks = document.getElementById("dayFailedChecks");
const dayPercentChart = document.getElementById("dayPercentChart");
const dayOffenseLevelChart = document.getElementById("dayOffenseLevelChart");

refreshDashboardButton.addEventListener("click", loadDashboardStatistics);

if (closeDayStatisticsModalButton) {
	closeDayStatisticsModalButton.addEventListener("click", closeDayStatisticsModal);
}

if (confirmDayStatisticsModalButton) {
	confirmDayStatisticsModalButton.addEventListener("click", closeDayStatisticsModal);
}

if (dayStatisticsModalOverlay) {
	dayStatisticsModalOverlay.addEventListener("click", (event) => {
		if (event.target === dayStatisticsModalOverlay) {
			closeDayStatisticsModal();
		}
	});
}

document.addEventListener("DOMContentLoaded", loadDashboardStatistics);

async function loadDashboardStatistics() {
	try {
		const response = await fetch("/dashboard/statistics?days=14");
		const statistics = await response.json();

		if (!response.ok) {
			renderDashboardError(statistics);
			return;
		}

		renderSummary(statistics.summary);
		renderActiveProvider(statistics.active_provider);
		renderActivePrompt(statistics.active_prompt);
		renderWarnings(statistics.warnings || []);
		renderVerdictDistribution(statistics.verdict_distribution);
		renderOffenseLevelDistribution(statistics.offense_level_distribution);
		renderChecksByDay(statistics.checks_by_day);
	} catch (error) {
		renderDashboardError(error);
	}
}

function renderSummary(summary) {
	totalChecksMetric.textContent = formatNumber(summary.total_checks);
	offensiveChecksMetric.textContent = formatNumber(summary.offensive_checks);
	nonOffensiveChecksMetric.textContent = formatNumber(summary.non_offensive_checks);
	failedChecksMetric.textContent = formatNumber(summary.failed_checks);

	averageProcessingTimeMetric.textContent = summary.average_processing_time_ms === null
		? "-"
		: `${Math.round(summary.average_processing_time_ms)} ms`;
}

function renderActiveProvider(provider) {
	if (!provider) {
		activeProviderStatus.innerHTML = `
			<div class="status-title danger-text">Не настроен</div>
			<div class="status-subtitle">Создай активный AI provider в настройках.</div>
		`;
		return;
	}

	activeProviderStatus.innerHTML = `
		<div class="status-title">${escapeHtml(provider.name)}</div>
		<div class="status-subtitle">${escapeHtml(provider.model_name)} · ${escapeHtml(provider.provider_type)}</div>
		<div class="status-code">${escapeHtml(provider.provider_url)}</div>
	`;
}

function renderActivePrompt(prompt) {
	if (!prompt) {
		activePromptStatus.innerHTML = `
			<div class="status-title danger-text">Не настроен</div>
			<div class="status-subtitle">Создай активный prompt template.</div>
		`;
		return;
	}

	activePromptStatus.innerHTML = `
		<div class="status-title">${escapeHtml(prompt.name)}</div>
		<div class="status-subtitle">${escapeHtml(prompt.code)} · version ${escapeHtml(prompt.version)}</div>
		<div class="status-code">${escapeHtml(prompt.length)} chars</div>
	`;
}

function renderVerdictDistribution(distribution) {
	verdictDistributionChart.innerHTML = "";

	const maxValue = Math.max(...distribution.map(item => item.value), 1);

	for (const item of distribution) {
		const percent = Math.round((item.value / maxValue) * 100);
		const label = getVerdictLabel(item.name);
		const className = getVerdictClass(item.name);

		const row = document.createElement("div");
		row.className = "bar-row";
		row.innerHTML = `
			<div class="bar-label">${escapeHtml(label)}</div>
			<div class="bar-track">
				<div class="bar-fill ${className}" style="width: ${percent}%"></div>
			</div>
			<div class="bar-value">${escapeHtml(item.value)}</div>
		`;

		verdictDistributionChart.appendChild(row);
	}
}

function renderOffenseLevelDistribution(distribution) {
	offenseLevelChart.innerHTML = "";

	const maxValue = Math.max(...distribution.map(item => item.count), 1);

	for (const item of distribution) {
		const percent = Math.round((item.count / maxValue) * 100);

		const column = document.createElement("div");
		column.className = "level-column";
		column.innerHTML = `
			<div class="level-bar-wrap">
				<div class="level-bar" style="height: ${percent}%"></div>
			</div>
			<div class="level-count">${escapeHtml(item.count)}</div>
			<div class="level-label">${escapeHtml(item.level)}</div>
		`;

		offenseLevelChart.appendChild(column);
	}
}

function renderChecksByDay(days) {
	checksByDayChart.innerHTML = "";

	const maxValue = Math.max(...days.map(item => item.total), 1);

	for (const day of days) {
		const totalPercent = Math.round((day.total / maxValue) * 100);
		const failedPercent = day.total === 0
			? 0
			: Math.round((day.failed / day.total) * 100);

		const row = document.createElement("button");
		row.className = "daily-row daily-row-button";
		row.type = "button";

		row.innerHTML = `
			<div class="daily-date">${escapeHtml(formatShortDate(day.date))}</div>
			<div class="daily-track">
				<div class="daily-fill" style="width: ${totalPercent}%"></div>
				<div class="daily-failed-fill" style="width: ${failedPercent}%"></div>
			</div>
			<div class="daily-value">
				<span>${escapeHtml(day.total)}</span>
				<small>${escapeHtml(day.failed)} ошибок</small>
			</div>
		`;

		row.addEventListener("click", () => {
			openDayStatisticsModal(day.date);
		});

		checksByDayChart.appendChild(row);
	}
}

function renderDashboardError(error) {
	const errorText = error instanceof Error
		? error.message
		: JSON.stringify(error, null, 2);

	totalChecksMetric.textContent = "-";
	offensiveChecksMetric.textContent = "-";
	nonOffensiveChecksMetric.textContent = "-";
	failedChecksMetric.textContent = "-";
	averageProcessingTimeMetric.textContent = "-";

	activeProviderStatus.innerHTML = `
		<div class="status-title danger-text">Ошибка</div>
		<div class="status-subtitle">${escapeHtml(errorText)}</div>
	`;

	activePromptStatus.innerHTML = `
		<div class="status-title danger-text">Ошибка</div>
		<div class="status-subtitle">Не удалось загрузить статистику.</div>
	`;

	verdictDistributionChart.innerHTML = "";
	offenseLevelChart.innerHTML = "";
	checksByDayChart.innerHTML = "";

	dashboardWarnings.innerHTML = `
		<div class="warning-card danger">
			<div class="warning-icon">!</div>
			<div>
				<strong>Ошибка загрузки Dashboard</strong>
				<span>${escapeHtml(errorText)}</span>
			</div>
		</div>
	`;
}

function getVerdictLabel(name) {
	if (name === "no_offensive") {
		return "No offensive";
	}

	if (name === "offensive") {
		return "Offensive";
	}

	if (name === "failed") {
		return "Failed";
	}

	return name;
}

function getVerdictClass(name) {
	if (name === "no_offensive") {
		return "success";
	}

	if (name === "offensive") {
		return "danger";
	}

	if (name === "failed") {
		return "warning";
	}

	return "";
}

function formatShortDate(value) {
	const date = new Date(value);

	if (Number.isNaN(date.getTime())) {
		return value;
	}

	return date.toLocaleDateString(undefined, {
		month: "short",
		day: "2-digit"
	});
}

function formatNumber(value) {
	if (value === null || value === undefined) {
		return "-";
	}

	return Number(value).toLocaleString();
}

async function openDayStatisticsModal(dateText) {
	dayStatisticsModalOverlay.classList.remove("hidden");
	renderDayStatisticsLoading(dateText);

	try {
		const response = await fetch(`/dashboard/statistics/day/${encodeURIComponent(dateText)}`);
		const statistics = await response.json();

		if (!response.ok) {
			renderDayStatisticsError(dateText, statistics);
			return;
		}

		renderDayStatistics(statistics);
	} catch (error) {
		renderDayStatisticsError(dateText, error);
	}
}

function closeDayStatisticsModal() {
	if (!dayStatisticsModalOverlay) {
		return;
	}

	dayStatisticsModalOverlay.classList.add("hidden");
}

function renderDayStatisticsLoading(dateText) {
	dayStatisticsTitle.textContent = `Статистика за ${dateText}`;
	dayTotalChecks.textContent = "-";
	dayOffensiveChecks.textContent = "-";
	dayNonOffensiveChecks.textContent = "-";
	dayFailedChecks.textContent = "-";
	dayPercentChart.innerHTML = `<div class="empty-state compact">Загрузка...</div>`;
	dayOffenseLevelChart.innerHTML = "";
}

function renderDayStatisticsError(dateText, error) {
	const errorText = error instanceof Error
		? error.message
		: JSON.stringify(error, null, 2);

	dayStatisticsTitle.textContent = `Статистика за ${dateText}`;
	dayTotalChecks.textContent = "-";
	dayOffensiveChecks.textContent = "-";
	dayNonOffensiveChecks.textContent = "-";
	dayFailedChecks.textContent = "-";

	dayPercentChart.innerHTML = `
		<div class="warning-card danger">
			<div class="warning-icon">!</div>
			<div>
				<strong>Ошибка загрузки статистики</strong>
				<span>${escapeHtml(errorText)}</span>
			</div>
		</div>
	`;

	dayOffenseLevelChart.innerHTML = "";
}

function renderDayStatistics(statistics) {
	const summary = statistics.summary;
	const percentages = statistics.percentages;

	dayStatisticsTitle.textContent = `Статистика за ${statistics.date}`;

	dayTotalChecks.textContent = formatNumber(summary.total_checks);
	dayOffensiveChecks.textContent = formatNumber(summary.offensive_checks);
	dayNonOffensiveChecks.textContent = formatNumber(summary.non_offensive_checks);
	dayFailedChecks.textContent = formatNumber(summary.failed_checks);

	renderDayPercentChart(percentages);
	renderDayOffenseLevelChart(statistics.offense_level_distribution);
}

function renderDayPercentChart(percentages) {
	const rows = [
		{
			name: "Нарушение",
			value: percentages.offensive_percent,
			className: "danger"
		},
		{
			name: "Без нарушения",
			value: percentages.non_offensive_percent,
			className: "success"
		},
		{
			name: "Ошибка",
			value: percentages.failed_percent,
			className: "warning"
		}
	];

	dayPercentChart.innerHTML = "";

	for (const row of rows) {
		const percent = Math.max(0, Math.min(Number(row.value || 0), 100));

		const element = document.createElement("div");
		element.className = "bar-row";
		element.innerHTML = `
			<div class="bar-label">${escapeHtml(row.name)}</div>
			<div class="bar-track">
				<div class="bar-fill ${row.className}" style="width: ${percent}%"></div>
			</div>
			<div class="bar-value">${escapeHtml(percent)}%</div>
		`;

		dayPercentChart.appendChild(element);
	}
}

function renderDayOffenseLevelChart(distribution) {
	dayOffenseLevelChart.innerHTML = "";

	const maxValue = Math.max(...distribution.map(item => item.count), 1);

	for (const item of distribution) {
		const percent = Math.round((item.count / maxValue) * 100);

		const column = document.createElement("div");
		column.className = "level-column";
		column.innerHTML = `
			<div class="level-bar-wrap">
				<div class="level-bar" style="height: ${percent}%"></div>
			</div>
			<div class="level-count">${escapeHtml(item.count)}</div>
			<div class="level-label">${escapeHtml(item.level)}</div>
		`;

		dayOffenseLevelChart.appendChild(column);
	}
}

function escapeHtml(value) {
	return String(value)
		.replaceAll("&", "&amp;")
		.replaceAll("<", "&lt;")
		.replaceAll(">", "&gt;")
		.replaceAll('"', "&quot;")
		.replaceAll("'", "&#039;");
}

function renderWarnings(warnings) {
	dashboardWarnings.innerHTML = "";

	if (!Array.isArray(warnings) || warnings.length === 0) {
		dashboardWarnings.innerHTML = `
			<div class="warning-card success">
				<div class="warning-icon">✓</div>
				<div>
					<strong>Критичных проблем не обнаружено</strong>
					<span>Сервис не вернул активных предупреждений.</span>
				</div>
			</div>
		`;
		return;
	}

	for (const warning of warnings) {
		const level = warning.level || "warning";
		const icon = getWarningIcon(level);

		const warningCard = document.createElement("div");
		warningCard.className = `warning-card ${level}`;

		warningCard.innerHTML = `
			<div class="warning-icon">${escapeHtml(icon)}</div>
			<div>
				<strong>${escapeHtml(warning.title)}</strong>
				<span>${escapeHtml(warning.description)}</span>
			</div>
		`;

		dashboardWarnings.appendChild(warningCard);
	}
}

function getWarningIcon(level) {
	if (level === "success") {
		return "✓";
	}

	if (level === "danger") {
		return "!";
	}

	return "!";
}

document.addEventListener("keydown", (event) => {
	if (event.key === "Escape") {
		closeDayStatisticsModal();
	}
});