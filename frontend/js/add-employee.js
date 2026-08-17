/* Create a new employee (admin only). */

requireAuth(true);

const addForm = document.getElementById("addEmployeeForm");
const addButton = document.getElementById("submitButton");
const successBox = document.getElementById("success");

addForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    showError("error", "");
    successBox.style.display = "none";
    addButton.disabled = true;

    try {
        const data = await api("/api/employees", {
            method: "POST",
            body: JSON.stringify({
                username: document.getElementById("username").value.trim(),
                password: document.getElementById("password").value,
                full_name: document.getElementById("full_name").value.trim(),
                department: document.getElementById("department").value.trim(),
                role: document.getElementById("role").value,
            }),
        });

        successBox.innerHTML =
            `<i class="fa-solid fa-circle-check"></i> ${data.message}`;
        successBox.style.display = "block";
        addForm.reset();
    } catch (error) {
        showError("error", error.message);
    } finally {
        addButton.disabled = false;
    }
});
