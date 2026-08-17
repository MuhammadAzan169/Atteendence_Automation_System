/* Admin employee list with delete. */

requireAuth(true);

const employeesBody = document.getElementById("employeesBody");

async function loadEmployees() {
    try {
        const data = await api("/api/employees");

        employeesBody.innerHTML = data.employees
            .map(
                (employee) => `
                <tr>
                    <td>${employee.id}</td>
                    <td>${escapeHtml(employee.username)}</td>
                    <td>${escapeHtml(employee.full_name)}</td>
                    <td>${escapeHtml(employee.department)}</td>
                    <td>${escapeHtml(employee.role)}</td>
                    <td>
                        <button class="btn-danger" data-delete="${employee.id}"
                                data-name="${escapeHtml(employee.username)}">
                            <i class="fa-solid fa-trash"></i>
                            Delete
                        </button>
                    </td>
                </tr>`
            )
            .join("");
    } catch (error) {
        employeesBody.innerHTML = "";
        showError("error", error.message);
    }
}

employeesBody.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-delete]");
    if (!button) return;

    const name = button.dataset.name;
    if (!confirm(`Delete employee "${name}" and all of their attendance?`)) {
        return;
    }

    button.disabled = true;

    try {
        await api(`/api/employees/${button.dataset.delete}`, {
            method: "DELETE",
        });
        showError("error", "");
        loadEmployees();
    } catch (error) {
        button.disabled = false;
        showError("error", error.message);
    }
});

loadEmployees();
