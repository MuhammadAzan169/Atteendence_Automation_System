/* Admin dashboard: statistics, filtering and exports. */

const admin = requireAuth(true);

if (admin) {
    setText("adminName", admin.username);
    loadStats();
    loadRecords();
}

async function loadStats() {
    try {
        const stats = await api("/api/admin/stats");
        setText("totalEmployees", stats.total_employees);
        setText("totalAttendance", stats.total_attendance);
        setText("presentToday", stats.present_today);
        setText("lateToday", stats.late_today);
    } catch (error) {
        showError("error", error.message);
    }
}

async function loadRecords() {
    const body = document.getElementById("recordsBody");
    const params = new URLSearchParams();

    const search = document.getElementById("search").value.trim();
    const date = document.getElementById("date").value;

    if (search) params.set("search", search);
    if (date) params.set("date", date);

    try {
        const data = await api(`/api/admin/attendance?${params.toString()}`);

        if (!data.records.length) {
            body.innerHTML =
                '<tr><td colspan="5">No matching attendance records.</td></tr>';
            return;
        }

        body.innerHTML = data.records
            .map(
                (record) => `
                <tr>
                    <td>${record.id}</td>
                    <td>${escapeHtml(record.employee_username)}</td>
                    <td>${escapeHtml(record.attendance_date)}</td>
                    <td>${escapeHtml(record.attendance_time)}</td>
                    <td>${statusBadge(record.status)}</td>
                </tr>`
            )
            .join("");
    } catch (error) {
        body.innerHTML = "";
        showError("error", error.message);
    }
}

document.getElementById("filterForm").addEventListener("submit", (event) => {
    event.preventDefault();
    loadRecords();
});

document.getElementById("resetFilters").addEventListener("click", () => {
    document.getElementById("search").value = "";
    document.getElementById("date").value = "";
    loadRecords();
});

// Downloads are plain links, so the token travels as a query parameter.
document.getElementById("exportExcel").addEventListener("click", () => {
    window.location.href = apiUrl("/api/reports/excel", true);
});

document.getElementById("exportPdf").addEventListener("click", () => {
    window.location.href = apiUrl("/api/reports/pdf", true);
});

document.getElementById("logoutButton").addEventListener("click", Auth.logout);
