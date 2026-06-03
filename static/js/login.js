const loginForm = document.getElementById("loginForm");
const loginMessage = document.getElementById("loginMessage");

loginForm.addEventListener("submit", async (event) => {
	event.preventDefault();

	clearLoginMessage();

	const username = document.getElementById("username").value;
	const password = document.getElementById("password").value;

	try {
		const response = await fetch("/login", {
			method: "POST",
			headers: {
				"Content-Type": "application/json"
			},
			body: JSON.stringify({
				username: username,
				password: password
			})
		});

		const responseBody = await response.json();

		if (!response.ok) {
			showLoginMessage(responseBody.detail || "Ошибка входа.", true);
			return;
		}

		window.location.href = responseBody.redirect_url || "/";
	} catch (error) {
		showLoginMessage(`Ошибка запроса: ${error}`, true);
	}
});

function showLoginMessage(message, isError) {
	loginMessage.classList.remove("hidden");
	loginMessage.className = isError ? "form-message error" : "form-message success";
	loginMessage.textContent = message;
}

function clearLoginMessage() {
	loginMessage.classList.add("hidden");
	loginMessage.textContent = "";
}