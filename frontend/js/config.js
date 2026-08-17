/*
 * Frontend configuration.
 *
 * Static hosting (Vercel) has no build-time environment variables for plain
 * HTML, so this file is the single place where the API URL lives.
 * After deploying the backend to Render, put its URL in API_BASE_URL below
 * (and in frontend/.env, which documents the same value).
 */

window.APP_CONFIG = {
  // Render backend URL, e.g. "https://attendance-api.onrender.com".
  // Leave empty to call the same origin that serves this page — which is what
  // you want when running everything locally through `python app.py`.
  API_BASE_URL: "https://atteendence-automation-system.onrender.com",

  APP_NAME: "Attendance Automation System",

  // Render's free tier sleeps after inactivity; the first request can take
  // ~30s to wake it. Shown to the user as a hint while waiting.
  COLD_START_HINT_MS: 4000,
};
