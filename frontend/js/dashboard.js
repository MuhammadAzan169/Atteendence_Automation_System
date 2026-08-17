/* Employee dashboard. */

const user = requireAuth();

if (user) {
    setText("welcomeName", user.full_name || user.username);

    if (user.role === "admin") {
        document.getElementById("adminLink").style.display = "block";
    }

    // ?success=1 is set after a successful attendance run.
    if (new URLSearchParams(window.location.search).get("success")) {
        document.getElementById("successMessage").style.display = "block";
    }

    document
        .getElementById("logoutButton")
        .addEventListener("click", Auth.logout);
}
