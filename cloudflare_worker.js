// Microfilm Archive — Rotation Sync Worker
// Deploy this to Cloudflare Workers.
// Add a secret environment variable named GITHUB_TOKEN with your GitHub PAT (repo scope).

const REPO    = 'markleyboyer/microfilm-archive';
const FILE    = 'rotations.json';
const GH_API  = `https://api.github.com/repos/${REPO}/contents/${FILE}`;
const GH_RAW  = `https://raw.githubusercontent.com/${REPO}/main/${FILE}`;

const CORS = {
  'Access-Control-Allow-Origin':  '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

export default {
  async fetch(request, env) {

    // Preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: CORS });
    }

    // GET — return current rotations
    if (request.method === 'GET') {
      const resp = await fetch(GH_RAW + '?t=' + Date.now());
      const body = resp.ok ? await resp.text() : '{}';
      return new Response(body, {
        headers: { ...CORS, 'Content-Type': 'application/json' }
      });
    }

    // POST — merge incoming rotations and save to GitHub
    if (request.method === 'POST') {
      let incoming;
      try {
        incoming = await request.json();
      } catch {
        return new Response('Invalid JSON', { status: 400, headers: CORS });
      }

      // Validate: must be a flat object with numeric degree values
      if (typeof incoming !== 'object' || Array.isArray(incoming)) {
        return new Response('Expected a JSON object', { status: 400, headers: CORS });
      }
      for (const [k, v] of Object.entries(incoming)) {
        if (typeof k !== 'string' || ![0, 90, 180, 270].includes(v)) {
          return new Response(`Invalid entry: ${k}=${v}`, { status: 400, headers: CORS });
        }
      }

      // Fetch current file + SHA from GitHub
      const ghHeaders = {
        'Authorization': `Bearer ${env.GITHUB_TOKEN}`,
        'Accept':        'application/vnd.github+json',
        'User-Agent':    'microfilm-rotation-worker',
        'X-GitHub-Api-Version': '2022-11-28',
      };

      let sha      = null;
      let existing = {};
      const current = await fetch(GH_API, { headers: ghHeaders });
      if (current.ok) {
        const meta = await current.json();
        sha      = meta.sha;
        existing = JSON.parse(atob(meta.content.replace(/\n/g, '')));
      }

      // Merge: incoming values override existing ones
      // Remove entries set to 0 (no rotation needed — keeps file tidy)
      const merged = { ...existing, ...incoming };
      for (const k of Object.keys(merged)) {
        if (merged[k] === 0) delete merged[k];
      }

      // Push to GitHub
      const payload = {
        message: `Update rotations (${Object.keys(merged).length} corrections)`,
        content: btoa(JSON.stringify(merged, null, 2)),
      };
      if (sha) payload.sha = sha;

      const push = await fetch(GH_API, {
        method:  'PUT',
        headers: { ...ghHeaders, 'Content-Type': 'application/json' },
        body:    JSON.stringify(payload),
      });

      if (push.ok) {
        return new Response(JSON.stringify({ ok: true, total: Object.keys(merged).length }), {
          headers: { ...CORS, 'Content-Type': 'application/json' }
        });
      } else {
        const err = await push.text();
        return new Response(err, { status: 502, headers: CORS });
      }
    }

    return new Response('Not found', { status: 404, headers: CORS });
  }
};
