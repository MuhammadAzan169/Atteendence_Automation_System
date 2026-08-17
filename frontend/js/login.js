/* Login page. */

const form = document.getElementById("loginForm");
const submitButton = document.getElementById("submitButton");

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    showError("error", "");
    submitButton.disabled = true;
    submitButton.innerHTML =
        '<i class="fa-solid fa-spinner fa-spin"></i> Signing in...';

    // Free hosting plans idle out; warn the user if the wait gets long.
    const hintTimer = setTimeout(() => {
        showError("hint", "Waking up the server, this can take a few seconds...");
    }, window.APP_CONFIG.COLD_START_HINT_MS);

    try {
        const data = await api("/api/auth/login", {
            method: "POST",
            body: JSON.stringify({
                username: document.getElementById("username").value.trim(),
                password: document.getElementById("password").value,
            }),
        });

        Auth.save(data.token, data.user);
        // Returns the page the user was sent away from — e.g. a scanned
        // attendance.html?qr=<code> — or the dashboard.
        window.location.href = takeDestination();
    } catch (error) {
        showError("error", error.message);
    } finally {
        clearTimeout(hintTimer);
        showError("hint", "");
        submitButton.disabled = false;
        submitButton.innerHTML =
            '<i class="fa-solid fa-arrow-right-to-bracket"></i> Login';
    }
});
