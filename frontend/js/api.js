/* Shared API client, token storage and page guards. */

const API_BASE = (window.APP_CONFIG.API_BASE_URL || "").replace(/\/$/, "");

/* An empty API_BASE means "same origin", which is only correct locally or
   behind the Docker nginx proxy. On a static host such as Vercel there is no
   API on this origin, so say so plainly instead of failing with a confusing
   network error later. */
(function checkConfiguration() {
  const isLocal = ["localhost", "127.0.0.1", ""].includes(
    window.location.hostname
  );
  const isProxied = window.location.port === "8080"; // docker-compose nginx

  if (API_BASE || isLocal || isProxied) return;

  const banner = document.createElement("p");
  banner.className = "message";
  banner.textContent =
    "Setup needed: set API_BASE_URL in js/config.js to your Render backend " +
    "URL, then redeploy.";
  window.addEventListener("DOMContentLoaded", () =>
    document.body.prepend(banner)
  );
})();
const TOKEN_KEY = "aas_token";
const USER_KEY = "aas_user";
const REDIRECT_KEY = "aas_redirect";

/* Remember where the user was heading so a login detour does not lose it.
   This matters most for QR scans: the poster opens
   attendance.html?qr=<code>, and that code must survive the login step. */
function rememberDestination() {
    const { pathname, search } = window.location;
    if (pathname.endsWith("login.html")) return;
    sessionStorage.setItem(REDIRECT_KEY, pathname.split("/").pop() + search);
}

function takeDestination(fallback = "dashboard.html") {
    const target = sessionStorage.getItem(REDIRECT_KEY);
    sessionStorage.removeItem(REDIRECT_KEY);
    return target || fallback;
}

const Auth = {
  get token() {
    return localStorage.getItem(TOKEN_KEY);
  },

  get user() {
    try {
      return JSON.parse(localStorage.getItem(USER_KEY) || "null");
    } catch (error) {
      return null;
    }
  },

  save(token, user) {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  },

  clear() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  },

  logout() {
    Auth.clear();
    window.location.href = "login.html";
  },
};

/* Build a full URL for an API path, including the token for direct links
   such as the Excel / PDF downloads. */
function apiUrl(path, withToken = false) {
  const url = `${API_BASE}${path}`;
  if (!withToken || !Auth.token) return url;
  const separator = url.includes("?") ? "&" : "?";
  return `${url}${separator}token=${encodeURIComponent(Auth.token)}`;
}

async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };

  if (options.body && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }
  if (Auth.token) {
    headers["Authorization"] = `Bearer ${Auth.token}`;
  }

  let response;
  try {
    response = await fetch(apiUrl(path), { ...options, headers });
  } catch (error) {
    throw new Error(
      "Cannot reach the server. If the backend is hosted on a free plan it " +
        "may be waking up — please try again in a moment."
    );
  }

  if (response.status === 401) {
    Auth.clear();
    if (!window.location.pathname.endsWith("login.html")) {
      rememberDestination();
      window.location.href = "login.html";
    }
    throw new Error("Your session expired. Please sign in again.");
  }

  const isJson = (response.headers.get("content-type") || "").includes(
    "application/json"
  );
  const payload = isJson ? await response.json() : null;

  if (!response.ok) {
    throw new Error((payload && payload.error) || "Something went wrong.");
  }

  return payload;
}

/* Redirect to the login page unless a valid session exists.
   Pass true to also require the admin role. */
function requireAuth(adminOnly = false) {
  const user = Auth.user;

  if (!Auth.token || !user) {
    rememberDestination();
    window.location.href = "login.html";
    return null;
  }

  if (adminOnly && user.role !== "admin") {
    window.location.href = "dashboard.html";
    return null;
  }

  return user;
}

/* Small helpers shared by the pages. */
function setText(id, value) {
  const element = document.getElementById(id);
  if (element) element.textContent = value;
}

function showError(id, message) {
  const element = document.getElementById(id);
  if (!element) return;
  element.textContent = message || "";
  element.style.display = message ? "block" : "none";
}

function escapeHtml(value) {
  return String(value ?? "").replace(
    /[&<>"']/g,
    (character) =>
      ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
      }[character])
  );
}

function statusBadge(status) {
  return status === "Present"
    ? '<span class="status-present"><i class="fa-solid fa-circle-check"></i> Present</span>'
    : '<span class="status-late"><i class="fa-solid fa-clock"></i> Late</span>';
}
