// Copy this file to config.js (which is git-ignored) and fill in your values.
// Without config.js the page works fine; it just doesn't sync to n8n.
const APP_CONFIG = {
    // Production webhook URL of the POST workflow in n8n (keep it local, don't commit it)
    syncUrl: "http://localhost:5678/webhook/REPLACE-WITH-YOUR-WEBHOOK-PATH",
    // Shared secret; must match the Header Auth credential on the n8n webhook node
    syncToken: "REPLACE-WITH-A-LONG-RANDOM-STRING"
};
