# n8n setup notes (security-relevant)

These steps harden the local n8n instance that receives progress counts from `index.html`
and serves them to `generate_chart.py`.

## 1. Bind n8n to localhost only

`-p 5678:5678` publishes the port on **all** network interfaces, so anyone on the same
Wi-Fi can reach your webhooks. Check what you have:

```bash
docker ps --format '{{.Names}}   {{.Ports}}'
# bad : 0.0.0.0:5678->5678/tcp
# good: 127.0.0.1:5678->5678/tcp
```

If it shows `0.0.0.0`, recreate the container **with the same data volume**. Look up the
volume first, otherwise you lose workflows, credentials and the data table:

```bash
docker inspect n8n --format '{{json .Mounts}}'     # note the volume name or host path
docker stop n8n && docker rm n8n                    # removes the container, not the volume
docker run -d --name n8n --restart unless-stopped \
  -p 127.0.0.1:5678:5678 \
  -v <YOUR_EXISTING_VOLUME>:/home/node/.n8n \
  docker.n8n.io/n8nio/n8n
```

(If you start n8n with docker compose, use `"127.0.0.1:5678:5678"` in `ports:`.)

## 2. Require a secret on both webhooks

For the POST webhook (progress from the browser) **and** the GET webhook (`current-score`):

1. Webhook node, **Authentication: Header Auth**.
2. Create a credential: *Name* `X-Api-Key`, *Value* a long random string
   (`openssl rand -hex 24`).
3. Put the same value in `config.js` (`syncToken`) and `.env` (`N8N_TOKEN`).
   Both files are git-ignored.

## 3. Validate the payload

`index.html` sends the four counts plus a `totals` object. Add a **Code** node
directly after the POST webhook, before the Data Table upsert:

```js
// Rejects anything that is not a sane set of counts. Passes the item through unchanged,
// so existing expressions like {{ $json.body.nomen }} keep working.
const body = $input.first().json.body ?? {};
const keys = ['nomen', 'adjektive', 'verben', 'praepositionen'];
const totals = body.totals ?? {};
for (const k of keys) {
  const v = body[k], max = totals[k];
  if (!Number.isInteger(v) || !Number.isInteger(max) || v < 0 || v > max || max > 5000) {
    throw new Error(`Invalid payload for "${k}"`);
  }
}
return $input.all();
```

## 4. Rotate the webhook path

The old webhook URL (a UUID path) has been in a public repo and in git history. Treat it
as burned: in the Webhook node, change the *Path* to a new random value, activate the
workflow, and put the new URL in `config.js` / `.env`. Deleting the URL from the code does
not remove it from history; rotating does.

## 5. CORS

With the token in place, the default CORS setting (`*`) is acceptable. Restricting
*Allowed Origins* is defense in depth, but a page opened from `file://` sends
`Origin: null`, so test before relying on it.

## 6. Exporting the workflow for the repo

*Workflow menu → Download* produces JSON without credential secrets, but it **does contain
the webhook path**. Replace the path with a placeholder (e.g. `REPLACE-ME`) before committing,
for example as `docs/n8n-workflow.json`.
