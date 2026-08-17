/* The signed-in employee's own attendance records. */

requireAuth();

const historyBody = document.getElementById("historyBody");

(async function load() {
    try {
        const data = await api("/api/attendance/history");

        if (!data.records.length) {
            historyBody.innerHTML =
                '<tr><td colspan="3">No attendance records yet.</td></tr>';
            return;
        }

        historyBody.innerHTML = data.records
            .map(
                (record) => `
                <tr>
                    <td>${escapeHtml(record.attendance_date)}</td>
                    <td>${escapeHtml(record.attendance_time)}</td>
                    <td>${statusBadge(record.status)}</td>
                </tr>`
            )
            .join("");
    } catch (error) {
        historyBody.innerHTML = "";
        showError("error", error.message);
    }
})();
