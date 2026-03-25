import os, re, json
from collections import defaultdict

base_dir = 'd:/Farmscape Weather Data/Microfilm processed'
images_dir = 'images'  # subfolder name, relative to base_dir

images_path = os.path.join(base_dir, images_dir)
scan_dir = images_path if os.path.isdir(images_path) else base_dir
files = [f for f in os.listdir(scan_dir) if f.endswith('.JPG') and '_' in f]

groups = defaultdict(list)
for f in sorted(files):
    suffix = f.rsplit('_', 1)[-1].replace('.JPG', '')
    m = re.match(r'^(\d{4}(?:-\d{4})?)(.+)$', suffix)
    if m:
        date, name = m.group(1), m.group(2)
        spaced = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        spaced = re.sub(r'([A-Z])([A-Z][a-z])', r'\1 \2', spaced)
        groups[(date, spaced)].append(f)

data = []
for (date, name), flist in sorted(groups.items()):
    data.append({'date': date, 'name': name, 'files': flist})

data_json = json.dumps(data)

html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Farmscape Weather Data - Microfilm Archive</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: Georgia, serif; background: #f5f0e8; color: #2c2416; }
  header { background: #2c2416; color: #f5f0e8; padding: 24px 32px; }
  header h1 { font-size: 1.5rem; font-weight: normal; letter-spacing: 0.05em; }
  header p { margin-top: 6px; font-size: 0.85rem; opacity: 0.7; }
  .controls { padding: 16px 32px; background: #ede8dc; border-bottom: 1px solid #c8bfa8; display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
  .controls input { flex: 1; min-width: 200px; padding: 9px 14px; border: 1px solid #b0a48a; border-radius: 4px; font-size: 0.95rem; background: #fffdf8; font-family: inherit; }
  .controls select { padding: 9px 14px; border: 1px solid #b0a48a; border-radius: 4px; font-size: 0.95rem; background: #fffdf8; font-family: inherit; }
  .stats { font-size: 0.85rem; color: #6b5e45; margin-left: auto; white-space: nowrap; }
  .view-toggle { display: flex; gap: 4px; }
  .view-toggle button { padding: 7px 12px; border: 1px solid #b0a48a; background: #fffdf8; border-radius: 4px; cursor: pointer; font-size: 0.85rem; color: #4a3c28; font-family: inherit; }
  .view-toggle button.active { background: #3d3020; color: #f5f0e8; border-color: #3d3020; }
  table { width: auto; border-collapse: collapse; }
  thead th { background: #3d3020; color: #f5f0e8; padding: 11px 16px; text-align: left; font-size: 0.8rem; letter-spacing: 0.08em; text-transform: uppercase; font-weight: normal; cursor: pointer; user-select: none; }
  thead th:hover { background: #52432e; }
  thead th.sorted-asc::after { content: " \u25b2"; }
  thead th.sorted-desc::after { content: " \u25bc"; }
  tbody tr.group-row { cursor: pointer; border-bottom: 1px solid #ddd6c4; transition: background 0.1s; }
  tbody tr.group-row:hover { background: #ede8dc; }
  tbody tr.group-row.expanded { background: #e5dfc9; }
  tbody tr.group-row td { padding: 10px 16px; font-size: 0.92rem; }
  td.count { text-align: right; color: #6b5e45; font-size: 0.85rem; white-space: nowrap; width: 1%; }
  td.date-col { font-variant-numeric: tabular-nums; color: #4a3c28; white-space: nowrap; width: 1%; }
  td.chevron { width: 28px; color: #9a8a6e; font-size: 0.75rem; transition: transform 0.2s; }
  tr.expanded td.chevron { transform: rotate(90deg); display: inline-block; }
  tr.files-row { display: none; background: #f8f4ec; }
  tr.files-row.visible { display: table-row; }
  tr.files-row td { padding: 14px 16px 20px 44px; border-bottom: 2px solid #c8bfa8; }
  .thumbnails { display: flex; flex-wrap: wrap; gap: 10px; }
  .thumb-item { display: flex; flex-direction: column; align-items: center; gap: 4px; }
  .thumb-img-wrap { position: relative; width: 90px; height: 70px; overflow: hidden; cursor: pointer; border: 1px solid #c8bfa8; border-radius: 3px; background: #e0d9cc; flex-shrink: 0; }
  .thumb-img-wrap img { position: absolute; top: 50%; left: 50%; transform-origin: center; transform: translate(-50%,-50%); width: 90px; height: 70px; object-fit: cover; transition: transform 0.2s; }
  .thumb-img-wrap:hover img { opacity: 0.88; }
  .thumb-btns { position: absolute; bottom: 0; left: 0; right: 0; display: flex; justify-content: center; gap: 3px; padding: 3px; background: rgba(0,0,0,0.55); opacity: 0; transition: opacity 0.15s; }
  .thumb-img-wrap:hover .thumb-btns { opacity: 1; }
  .rot-btn { padding: 2px 6px; background: rgba(255,255,255,0.92); border: none; border-radius: 2px; cursor: pointer; font-size: 1rem; line-height: 1; color: #2c2416; }
  .rot-btn:hover { background: white; }
  .thumb-label { font-size: 0.62rem; color: #7a6e5a; max-width: 90px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; text-align: center; }
  .list-items { display: flex; flex-direction: column; gap: 0; }
  .list-item { display: flex; align-items: center; gap: 12px; padding: 5px 0; border-bottom: 1px solid #e8e2d4; }
  .list-item-img-wrap { position: relative; width: 48px; height: 38px; overflow: hidden; cursor: pointer; flex-shrink: 0; border: 1px solid #c8bfa8; border-radius: 2px; background: #e0d9cc; }
  .list-item-img-wrap img { position: absolute; top: 50%; left: 50%; transform-origin: center; transform: translate(-50%,-50%); width: 48px; height: 38px; object-fit: cover; transition: transform 0.2s; }
  .list-item .rot-btn { font-size: 0.85rem; padding: 2px 5px; background: #ede8dc; border: 1px solid #c8bfa8; border-radius: 2px; cursor: pointer; color: #4a3c28; }
  .list-item .rot-btn:hover { background: #ddd6c4; }
  .list-item-name { font-size: 0.85rem; color: #3d3020; cursor: pointer; flex: 1; }
  .list-item-name:hover { text-decoration: underline; }
  .no-results { padding: 40px; text-align: center; color: #9a8a6e; font-style: italic; }
  /* Selection toolbar */
  .group-toolbar { display: flex; align-items: center; gap: 7px; padding: 0 0 10px; flex-wrap: wrap; border-bottom: 1px solid #e0d9cc; margin-bottom: 12px; }
  .sel-info { font-size: 0.83rem; color: #4a3c28; white-space: nowrap; margin-right: 2px; }
  .tb-btn { padding: 5px 11px; border: 1px solid #b0a48a; background: #fffdf8; border-radius: 4px; cursor: pointer; font-size: 0.82rem; color: #4a3c28; font-family: inherit; white-space: nowrap; }
  .tb-btn:hover { background: #ede8dc; }
  .tb-btn.sel-all { border-color: #3d3020; color: #3d3020; }
  .tb-btn.rot-sel { background: #3d3020; color: #f5f0e8; border-color: #3d3020; }
  .tb-btn.rot-sel:hover { background: #52432e; }
  .tb-btn.desel { color: #7a6e5a; }
  .thumb-item.selected .thumb-img-wrap { box-shadow: 0 0 0 3px #4a7a4a; border-color: #4a7a4a; }
  .thumb-item.selected .thumb-label { color: #4a7a4a; font-weight: bold; }
  /* Lightbox */
  .lightbox { position: fixed; inset: 0; z-index: 1000; display: flex; align-items: center; justify-content: center; }
  .lightbox.hidden { display: none; }
  .lb-overlay { position: absolute; inset: 0; background: rgba(0,0,0,0.88); }
  .lb-box { position: relative; z-index: 1; display: flex; flex-direction: column; align-items: center; gap: 10px; }
  .lb-img-wrap { display: flex; align-items: center; justify-content: center; width: 90vw; height: 80vh; overflow: hidden; cursor: zoom-in; }
  .lb-img-wrap.zoomed { cursor: grab; }
  .lb-img-wrap.dragging { cursor: grabbing; }
  .lb-img-wrap img { max-width: 90vw; max-height: 80vh; object-fit: contain; transform-origin: center; user-select: none; }
  .lb-bar { display: flex; align-items: center; gap: 6px; background: rgba(0,0,0,0.65); padding: 8px 12px; border-radius: 6px; }
  .lb-btn { padding: 6px 14px; background: #3d3020; color: #f5f0e8; border: none; border-radius: 4px; cursor: pointer; font-size: 1rem; font-family: inherit; white-space: nowrap; }
  .lb-btn:hover { background: #52432e; }
  .lb-btn:disabled { opacity: 0.35; cursor: default; }
  .lb-btn.close { background: #6b2020; margin-left: 8px; }
  .lb-btn.close:hover { background: #8b3030; }
  .lb-counter { color: #ccc; font-size: 0.85rem; padding: 0 8px; white-space: nowrap; }
  .lb-label { color: #aaa; font-size: 0.72rem; max-width: 90vw; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  /* Help modal */
  .help-btn { padding: 7px 13px; border: 1px solid #b0a48a; background: #fffdf8; border-radius: 50%; cursor: pointer; font-size: 0.95rem; color: #4a3c28; font-family: inherit; font-weight: bold; line-height: 1; flex-shrink: 0; }
  .help-btn:hover { background: #ede8dc; }
  .help-modal { position: fixed; inset: 0; z-index: 2000; display: flex; align-items: center; justify-content: center; }
  .help-modal.hidden { display: none; }
  .help-overlay { position: absolute; inset: 0; background: rgba(0,0,0,0.6); }
  .help-box { position: relative; z-index: 1; background: #fffdf8; border-radius: 8px; max-width: 680px; width: 92vw; max-height: 85vh; overflow-y: auto; box-shadow: 0 8px 40px rgba(0,0,0,0.4); }
  .help-box header { background: #2c2416; color: #f5f0e8; padding: 20px 28px; border-radius: 8px 8px 0 0; display: flex; justify-content: space-between; align-items: center; }
  .help-box header h2 { font-size: 1.1rem; font-weight: normal; letter-spacing: 0.04em; }
  .help-close { background: none; border: none; color: #f5f0e8; font-size: 1.3rem; cursor: pointer; padding: 0 4px; opacity: 0.8; }
  .help-close:hover { opacity: 1; }
  .help-body { padding: 24px 28px; }
  .help-body h3 { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.1em; color: #6b5e45; margin: 22px 0 8px; border-bottom: 1px solid #e0d9cc; padding-bottom: 4px; }
  .help-body h3:first-child { margin-top: 0; }
  .help-body p { font-size: 0.9rem; line-height: 1.65; color: #3a2e1e; margin-bottom: 8px; }
  .help-body ul { padding-left: 18px; margin-bottom: 8px; }
  .help-body li { font-size: 0.9rem; line-height: 1.65; color: #3a2e1e; margin-bottom: 3px; }
  .help-body kbd { display: inline-block; padding: 1px 7px; background: #e8e2d4; border: 1px solid #b0a48a; border-radius: 3px; font-family: monospace; font-size: 0.82rem; color: #2c2416; }
  .help-body .tip { background: #f0ece0; border-left: 3px solid #b0a48a; padding: 8px 12px; border-radius: 0 4px 4px 0; margin: 10px 0; font-size: 0.88rem; color: #4a3c28; line-height: 1.5; }
  .folder-btn { display: inline-flex; align-items: center; gap: 8px; padding: 8px 16px; background: #3d3020; color: #f5f0e8; border-radius: 4px; cursor: pointer; font-size: 0.88rem; font-family: inherit; letter-spacing: 0.03em; white-space: nowrap; }
  .folder-btn:hover { background: #52432e; }
  .folder-status { font-size: 0.85rem; color: #6b5e45; white-space: nowrap; }
  .folder-status.loaded { color: #4a7a4a; font-weight: bold; }
</style>
</head>
<body>
<header>
  <h1>Farmscape Weather Data &mdash; Microfilm Archive</h1>
  <p>New York Academy Reports &bull; 1827&ndash;1860 &bull; Click any row to browse its files</p>
</header>
<div class="controls">
  <button class="folder-btn" id="folderBtn" onclick="pickFolder()">&#128193; Select Images Folder</button>
  <input type="file" id="folderFallback" webkitdirectory style="display:none">
  <span class="folder-status loaded" id="folderStatus">Serving from cloud &mdash; select local folder to override</span>
  <input type="text" id="search" placeholder="Search academy name or year..." oninput="applyFilters()">
  <select id="yearFilter" onchange="applyFilters()">
    <option value="">All years</option>
  </select>
  <div class="view-toggle">
    <button id="btnThumb" class="active" onclick="setView('thumb')">Thumbnails</button>
    <button id="btnList" onclick="setView('list')">List</button>
  </div>
  <span class="stats" id="stats"></span>
  <span id="syncStatus" style="font-size:0.82rem;min-width:80px;text-align:right"></span>
  <button class="help-btn" onclick="document.getElementById('helpModal').classList.remove('hidden')" title="User guide">?</button>
</div>
<table id="mainTable">
  <thead>
    <tr>
      <th style="width:28px;cursor:default"></th>
      <th onclick="sortBy('name')" id="th-name">Academy</th>
      <th onclick="sortBy('date')" id="th-date" style="white-space:nowrap;width:1%">Year</th>
      <th onclick="sortBy('count')" id="th-count" style="text-align:right;white-space:nowrap;width:1%">Files</th>
    </tr>
  </thead>
  <tbody id="tbody"></tbody>
</table>
<div id="noResults" class="no-results" style="display:none">No matching records found.</div>

<script type="application/json" id="archiveData">""" + data_json + """</script>

<script>
let DATA = [];
const R2_BASE   = 'https://pub-e96a83f726634e6a8bac05a0641d11fe.r2.dev/images/';
const R2_THUMBS = 'https://pub-e96a83f726634e6a8bac05a0641d11fe.r2.dev/thumbs/';

let currentSort = { key: 'date', dir: 1 };
let viewMode = 'thumb';
const fileMap = {};

// ── IndexedDB helpers ────────────────────────────────────────────────────────
function openDB() {
  return new Promise((res, rej) => {
    const r = indexedDB.open('microfilm_viewer', 1);
    r.onupgradeneeded = e => e.target.result.createObjectStore('data');
    r.onsuccess = e => res(e.target.result);
    r.onerror   = e => rej(e.target.error);
  });
}
async function dbPut(key, val) {
  const db = await openDB();
  return new Promise((res, rej) => {
    const tx = db.transaction('data', 'readwrite');
    tx.objectStore('data').put(val, key);
    tx.oncomplete = res; tx.onerror = rej;
  });
}
async function dbGet(key) {
  const db = await openDB();
  return new Promise((res, rej) => {
    const tx  = db.transaction('data', 'readonly');
    const req = tx.objectStore('data').get(key);
    req.onsuccess = () => res(req.result); req.onerror = rej;
  });
}

// ── Folder loading ───────────────────────────────────────────────────────────
function resetOpenRows() {
  document.querySelectorAll('.files-row td').forEach(cell => { cell.dataset.loaded = ''; cell.innerHTML = ''; });
  document.querySelectorAll('.files-row.visible').forEach(row => {
    row.classList.remove('visible');
    row.previousElementSibling.classList.remove('expanded');
  });
}

async function loadFromHandle(handle) {
  const status = document.getElementById('folderStatus');
  status.className = 'folder-status';
  status.textContent = 'Scanning\u2026';
  Object.values(fileMap).forEach(url => URL.revokeObjectURL(url));
  Object.keys(fileMap).forEach(k => delete fileMap[k]);
  resetOpenRows();

  // Collect file handles
  const handles = [];
  try {
    for await (const entry of handle.values()) {
      if (entry.kind === 'file' && entry.name.toUpperCase().endsWith('.JPG') && entry.name.includes('_'))
        handles.push(entry);
    }
  } catch (e) { status.textContent = 'Error reading folder.'; return; }

  // Resolve File objects in batches
  const BATCH = 300;
  for (let i = 0; i < handles.length; i += BATCH) {
    const files = await Promise.all(handles.slice(i, i + BATCH).map(h => h.getFile()));
    files.forEach(f => { fileMap[f.name] = URL.createObjectURL(f); });
    status.textContent = 'Loading\u2026 ' + Math.min(i + BATCH, handles.length).toLocaleString() + ' / ' + handles.length.toLocaleString();
    await new Promise(r => setTimeout(r, 0));
  }

  const count = Object.keys(fileMap).length;
  status.textContent = handle.name + ' \u2014 ' + count.toLocaleString() + ' images loaded';
  status.className = 'folder-status loaded';
  document.getElementById('folderBtn').textContent = '\\u{1F4C1} ' + handle.name;
}

// Fallback for browsers without showDirectoryPicker (e.g. Firefox)
function loadFromFileList(fileList) {
  const status = document.getElementById('folderStatus');
  status.className = 'folder-status';
  status.textContent = 'Loading\u2026';
  Object.values(fileMap).forEach(url => URL.revokeObjectURL(url));
  Object.keys(fileMap).forEach(k => delete fileMap[k]);
  resetOpenRows();
  const all = Array.from(fileList);
  const BATCH = 500;
  let i = 0;
  function next() {
    for (let end = Math.min(i + BATCH, all.length); i < end; i++)
      fileMap[all[i].name] = URL.createObjectURL(all[i]);
    status.textContent = 'Loading\u2026 ' + i.toLocaleString() + ' / ' + all.length.toLocaleString();
    if (i < all.length) setTimeout(next, 0);
    else { status.textContent = i.toLocaleString() + ' images loaded'; status.className = 'folder-status loaded'; }
  }
  setTimeout(next, 0);
}

document.getElementById('folderFallback').addEventListener('change', e => loadFromFileList(e.target.files));

async function pickFolder() {
  if (window.showDirectoryPicker) {
    try {
      const handle = await window.showDirectoryPicker({ mode: 'read' });
      await dbPut('folderHandle', handle);
      await loadFromHandle(handle);
    } catch (e) { if (e.name !== 'AbortError') console.error(e); }
  } else {
    document.getElementById('folderFallback').click();
  }
}

// ── Restore last folder on page load ────────────────────────────────────────
(async function tryRestore() {
  if (!window.showDirectoryPicker) return;
  try {
    const handle = await dbGet('folderHandle');
    if (!handle) return;
    const perm = await handle.queryPermission({ mode: 'read' });
    if (perm === 'granted') {
      // Same session or Chrome persisted permission — load silently
      await loadFromHandle(handle);
    } else if (perm === 'prompt') {
      // Need one click to re-grant — update button text so user knows
      const btn = document.getElementById('folderBtn');
      btn.textContent = '\u21A9 Re-open \u201C' + handle.name + '\u201D';
      document.getElementById('folderStatus').textContent = 'Click to reload last folder';
      btn.onclick = async () => {
        try {
          await handle.requestPermission({ mode: 'read' });
          btn.textContent = '\\u{1F4C1} Select Images Folder';
          btn.onclick = pickFolder;
          await dbPut('folderHandle', handle);
          await loadFromHandle(handle);
        } catch (e) { if (e.name !== 'AbortError') console.error(e); }
      };
    }
  } catch (e) { /* no stored handle or IDB error — ignore */ }
})();

// Year filter populated after data loads (see deferred init below)

function fileUrl(fname) {
  return fileMap[fname] || R2_BASE + encodeURIComponent(fname);
}
function thumbUrl(fname) {
  return fileMap[fname] || R2_THUMBS + encodeURIComponent(fname);
}

function sortBy(key) {
  if (currentSort.key === key) { currentSort.dir *= -1; }
  else { currentSort.key = key; currentSort.dir = 1; }
  ['name','date','count'].forEach(k => {
    const th = document.getElementById('th-' + k);
    th.className = (currentSort.key === k)
      ? (currentSort.dir === 1 ? 'sorted-asc' : 'sorted-desc') : '';
  });
  applyFilters();
}

function applyFilters() {
  const q = document.getElementById('search').value.trim().toLowerCase();
  const yr = document.getElementById('yearFilter').value;
  let filtered = DATA.filter(g =>
    (!q || g.name.toLowerCase().includes(q) || g.date.includes(q)) &&
    (!yr || g.date === yr)
  );
  const key = currentSort.key;
  filtered.sort((a, b) => {
    let va = key === 'count' ? a.files.length : (key === 'date' ? a.date : a.name.toLowerCase());
    let vb = key === 'count' ? b.files.length : (key === 'date' ? b.date : b.name.toLowerCase());
    return (va < vb ? -1 : va > vb ? 1 : 0) * currentSort.dir;
  });
  render(filtered);
}

function render(rows) {
  const tbody = document.getElementById('tbody');
  tbody.innerHTML = '';
  const nr = document.getElementById('noResults');
  nr.style.display = rows.length ? 'none' : 'block';
  const total = rows.reduce((s, g) => s + g.files.length, 0);
  document.getElementById('stats').textContent =
    rows.length.toLocaleString() + ' groups \u00b7 ' + total.toLocaleString() + ' files';

  // Build rows in batches so the browser can paint between chunks
  const BATCH = 60;
  let i = 0;
  function renderBatch() {
    const frag = document.createDocumentFragment();
    for (let end = Math.min(i + BATCH, rows.length); i < end; i++) {
      const g = rows[i];
      const tr = document.createElement('tr');
      tr.className = 'group-row';
      tr.innerHTML =
        '<td class="chevron">&#9654;</td>' +
        '<td>' + g.name + '</td>' +
        '<td class="date-col">' + g.date + '</td>' +
        '<td class="count">' + g.files.length + '</td>';

      const filesRow = document.createElement('tr');
      filesRow.className = 'files-row';
      filesRow.innerHTML = '<td colspan="4"></td>';

      tr.addEventListener('click', function() {
        const open = filesRow.classList.contains('visible');
        if (open) {
          filesRow.classList.remove('visible');
          tr.classList.remove('expanded');
        } else {
          tr.classList.add('expanded');
          filesRow.classList.add('visible');
          loadFiles(filesRow.querySelector('td'), g);
        }
      });

      frag.appendChild(tr);
      frag.appendChild(filesRow);
    }
    tbody.appendChild(frag);
    if (i < rows.length) requestAnimationFrame(renderBatch);
  }
  renderBatch();
}

function makeRotBtn(symbol, title, fname, delta) {
  const btn = document.createElement('button');
  btn.className = 'rot-btn';
  btn.title = title;
  btn.textContent = symbol;
  btn.addEventListener('click', e => { e.stopPropagation(); rotate(fname, delta); });
  return btn;
}

function loadFiles(cell, g) {
  if (cell.dataset.loaded) return;
  cell.dataset.loaded = '1';

  if (viewMode === 'thumb') {
    // ── Toolbar (always visible) ───────────────────────────────────────────
    const toolbar = document.createElement('div');
    toolbar.className = 'group-toolbar';

    // Rotate All buttons — always shown
    const btnRotAllL = document.createElement('button'); btnRotAllL.className = 'tb-btn rot-sel'; btnRotAllL.textContent = '\\u21ba Rotate All Left';
    const btnRotAllR = document.createElement('button'); btnRotAllR.className = 'tb-btn rot-sel'; btnRotAllR.textContent = '\\u21bb Rotate All Right';
    btnRotAllL.addEventListener('click', () => g.files.forEach(f => rotate(f, -90)));
    btnRotAllR.addEventListener('click', () => g.files.forEach(f => rotate(f,  90)));

    // Divider
    const div1 = document.createElement('span');
    div1.style.cssText = 'border-left:1px solid #c8bfa8;height:1.2em;margin:0 2px';

    // Selection buttons — shown only when something is selected
    const info      = document.createElement('span');       info.className      = 'sel-info';
    const btnSelAll = document.createElement('button');     btnSelAll.className = 'tb-btn sel-all'; btnSelAll.textContent = 'Select All';
    const btnDesel  = document.createElement('button');     btnDesel.className  = 'tb-btn desel';   btnDesel.textContent  = 'Deselect All';
    const btnRotL   = document.createElement('button');     btnRotL.className   = 'tb-btn rot-sel'; btnRotL.textContent   = '\\u21ba Rotate Selected';
    const btnRotR   = document.createElement('button');     btnRotR.className   = 'tb-btn rot-sel'; btnRotR.textContent   = '\\u21bb Rotate Selected';
    const selGroup  = [info, btnDesel, btnRotL, btnRotR];
    selGroup.forEach(el => { el.classList.add('sel-only'); el.style.display = 'none'; });

    btnSelAll.addEventListener('click', () => { g.files.forEach(f => getSel(g).add(f)); updateSelUI(g, cell); });
    btnDesel.addEventListener('click',  () => { getSel(g).clear(); updateSelUI(g, cell); });
    btnRotL.addEventListener('click',   () => getSel(g).forEach(f => rotate(f, -90)));
    btnRotR.addEventListener('click',   () => getSel(g).forEach(f => rotate(f,  90)));

    toolbar._info     = info;
    toolbar._selGroup = selGroup;

    toolbar.appendChild(btnRotAllL);
    toolbar.appendChild(btnRotAllR);
    toolbar.appendChild(div1);
    toolbar.appendChild(btnSelAll);
    toolbar.appendChild(info);
    toolbar.appendChild(btnDesel);
    toolbar.appendChild(btnRotL);
    toolbar.appendChild(btnRotR);
    cell._toolbar = toolbar;
    cell.appendChild(toolbar);

    // ── Thumbnails ─────────────────────────────────────────────────────────
    const wrap = document.createElement('div');
    wrap.className = 'thumbnails';
    g.files.forEach((f, idx) => {
      const url   = fileUrl(f);
      const label = f.replace(/^IMG_\\d+ ?(\\(\\d+\\))?_/, '').replace('.JPG', '');

      const item = document.createElement('div');
      item.className = 'thumb-item';
      item.dataset.fname = f;

      // Image wrapper — click opens lightbox or toggles selection
      const imgWrap = document.createElement('div');
      imgWrap.className = 'thumb-img-wrap';
      imgWrap.addEventListener('click', e => {
        if (e.ctrlKey || e.metaKey) {
          // Ctrl/Cmd+click: toggle this image
          const sel = getSel(g);
          sel.has(f) ? sel.delete(f) : sel.add(f);
          updateSelUI(g, cell);
        } else if (e.shiftKey) {
          // Shift+click: range select from last clicked
          const sel  = getSel(g);
          const last = lastClickIdx[gKey(g)];
          const from = last !== undefined ? Math.min(last, idx) : 0;
          const to   = last !== undefined ? Math.max(last, idx) : idx;
          for (let i = from; i <= to; i++) sel.add(g.files[i]);
          updateSelUI(g, cell);
        } else {
          openLightbox(g, idx);
        }
        lastClickIdx[gKey(g)] = idx;
      });

      const img = document.createElement('img');
      img.loading = 'lazy';
      img.dataset.fname = f;
      img.alt = f;
      img.src = thumbUrl(f);
      applyImgRotation(img);

      const btns = document.createElement('div');
      btns.className = 'thumb-btns';
      btns.appendChild(makeRotBtn('\\u21ba', 'Rotate left',  f, -90));
      btns.appendChild(makeRotBtn('\\u21bb', 'Rotate right', f,  90));

      imgWrap.appendChild(img);
      imgWrap.appendChild(btns);

      const labelEl = document.createElement('span');
      labelEl.className = 'thumb-label';
      labelEl.title = f;
      labelEl.textContent = label;

      item.appendChild(imgWrap);
      item.appendChild(labelEl);
      wrap.appendChild(item);
    });
    cell.appendChild(wrap);

  } else {
    const wrap = document.createElement('div');
    wrap.className = 'list-items';
    g.files.forEach((f, idx) => {
      const url = fileUrl(f);
      const item = document.createElement('div');
      item.className = 'list-item';

      // Small image — click opens lightbox
      const imgWrap = document.createElement('div');
      imgWrap.className = 'list-item-img-wrap';
      imgWrap.addEventListener('click', () => openLightbox(g, idx));

      const img = document.createElement('img');
      img.loading = 'lazy';
      img.dataset.fname = f;
      img.alt = f;
      img.src = thumbUrl(f);
      applyImgRotation(img);
      imgWrap.appendChild(img);

      // Filename — click opens lightbox
      const name = document.createElement('span');
      name.className = 'list-item-name';
      name.textContent = f;
      name.addEventListener('click', () => openLightbox(g, idx));

      item.appendChild(imgWrap);
      item.appendChild(makeRotBtn('\\u21ba', 'Rotate left',  f, -90));
      item.appendChild(makeRotBtn('\\u21bb', 'Rotate right', f,  90));
      item.appendChild(name);
      wrap.appendChild(item);
    });
    cell.appendChild(wrap);
  }
}

function setView(mode) {
  viewMode = mode;
  document.getElementById('btnThumb').classList.toggle('active', mode === 'thumb');
  document.getElementById('btnList').classList.toggle('active', mode === 'list');
  // Close all open rows so they re-render with new view on next open
  document.querySelectorAll('.files-row.visible').forEach(row => {
    row.classList.remove('visible');
    row.previousElementSibling.classList.remove('expanded');
  });
  document.querySelectorAll('.files-row td').forEach(cell => {
    cell.dataset.loaded = '';
    cell.innerHTML = '';
  });
}

// ── Selection state ──────────────────────────────────────────────────────────
const selections   = {}; // groupKey -> Set of filenames
const lastClickIdx = {}; // groupKey -> index of last clicked thumb

function gKey(g) { return g.date + '||' + g.name; }
function getSel(g) {
  const k = gKey(g);
  if (!selections[k]) selections[k] = new Set();
  return selections[k];
}

function updateSelUI(g, cell) {
  const sel     = getSel(g);
  const toolbar = cell._toolbar;
  if (!toolbar) return;
  const hasAny  = sel.size > 0;
  toolbar._selGroup.forEach(el => el.style.display = hasAny ? '' : 'none');
  if (hasAny) toolbar._info.textContent = sel.size + ' of ' + g.files.length + ' selected \u2014';
  cell.querySelectorAll('.thumb-item[data-fname]').forEach(item => {
    item.classList.toggle('selected', sel.has(item.dataset.fname));
  });
}

// ── Rotation state — synced to GitHub via Cloudflare Worker ─────────────────
const WORKER_URL = 'https://microfilm-rotations.square-star-6696.workers.dev';
const rotations  = {};
let   pushTimer  = null;

// Load rotations from GitHub on page load
(async function loadRotations() {
  try {
    const resp = await fetch('https://raw.githubusercontent.com/markleyboyer/microfilm-archive/main/rotations.json?t=' + Date.now());
    if (resp.ok) {
      const data = await resp.json();
      Object.assign(rotations, data);
      // Apply to any images already visible
      document.querySelectorAll('img[data-fname]').forEach(applyImgRotation);
    }
  } catch(e) { /* rotations.json not created yet — that's fine */ }
})();

function setSyncStatus(msg, color) {
  const el = document.getElementById('syncStatus');
  if (!el) return;
  el.textContent = msg;
  el.style.color = color;
  if (msg) setTimeout(() => { if (el.textContent === msg) el.textContent = ''; }, 3000);
}

function schedulePush() {
  clearTimeout(pushTimer);
  pushTimer = setTimeout(async () => {
    setSyncStatus('Saving\u2026', '#6b5e45');
    try {
      const resp = await fetch(WORKER_URL + '/rotations', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(rotations),
      });
      if (resp.ok) setSyncStatus('Saved \u2713', '#4a7a4a');
      else         setSyncStatus('Save failed', '#8b3030');
    } catch(e) {   setSyncStatus('Save failed', '#8b3030'); }
  }, 1500);
}

function getRotation(fname) { return rotations[fname] || 0; }

function rotate(fname, delta) {
  rotations[fname] = ((getRotation(fname) + delta) + 360) % 360;
  if (rotations[fname] === 0) delete rotations[fname];
  schedulePush();
  // Update all visible thumbnail/list images for this file
  document.querySelectorAll('img[data-fname]').forEach(img => {
    if (img.dataset.fname === fname) applyImgRotation(img);
  });
  // Sync lightbox if it's showing this file
  if (!document.getElementById('lightbox').classList.contains('hidden')) {
    const lbImg = document.getElementById('lb-img');
    if (lbImg.dataset.fname === fname) applyLbRotation(lbImg);
  }
}

function applyImgRotation(img) {
  const deg = getRotation(img.dataset.fname);
  const swap = deg === 90 || deg === 270;
  const base = 'translate(-50%,-50%) rotate(' + deg + 'deg)';
  img.style.transform = swap ? base + ' scale(0.78)' : base;
}

// Lightbox zoom/pan state
const lb = { group: null, idx: 0 };
let lbZoom = 1, lbPanX = 0, lbPanY = 0;

function applyLbRotation(img) {
  const deg  = getRotation(img.dataset.fname);
  const swap = deg === 90 || deg === 270;
  img.style.maxWidth  = swap ? '80vh' : '90vw';
  img.style.maxHeight = swap ? '90vw' : '80vh';
  img.style.transform = 'translate(' + lbPanX + 'px,' + lbPanY + 'px) rotate(' + deg + 'deg) scale(' + lbZoom + ')';
  const wrap = document.querySelector('.lb-img-wrap');
  wrap.classList.toggle('zoomed', lbZoom > 1);
  const label = document.getElementById('lb-zoom-label');
  if (label) label.textContent = lbZoom === 1 ? '1\u00d7' : (Math.round(lbZoom * 10) / 10) + '\u00d7';
}

function lbZoomBy(factor) {
  lbZoom = Math.min(8, Math.max(1, lbZoom * factor));
  if (lbZoom === 1) { lbPanX = 0; lbPanY = 0; }
  applyLbRotation(document.getElementById('lb-img'));
}

function openLightbox(group, idx) {
  lb.group = group;
  lb.idx   = idx;
  updateLightbox();
  document.getElementById('lightbox').classList.remove('hidden');
  document.body.style.overflow = 'hidden';
}

function closeLightbox() {
  document.getElementById('lightbox').classList.add('hidden');
  document.body.style.overflow = '';
}

function lbNav(delta) {
  const n = lb.idx + delta;
  if (n >= 0 && n < lb.group.files.length) { lb.idx = n; updateLightbox(); }
}

function updateLightbox() {
  lbZoom = 1; lbPanX = 0; lbPanY = 0;
  const f   = lb.group.files[lb.idx];
  const img = document.getElementById('lb-img');
  img.src            = fileUrl(f);
  img.dataset.fname  = f;
  applyLbRotation(img);
  document.getElementById('lb-label').textContent   = f;
  document.getElementById('lb-counter').textContent = (lb.idx + 1) + ' / ' + lb.group.files.length;
  document.getElementById('lb-prev').disabled = lb.idx === 0;
  document.getElementById('lb-next').disabled = lb.idx === lb.group.files.length - 1;
}

document.addEventListener('keydown', e => {
  const lbOpen   = !document.getElementById('lightbox').classList.contains('hidden');
  const helpOpen = !document.getElementById('helpModal').classList.contains('hidden');
  if (helpOpen) {
    if (e.key === 'Escape') document.getElementById('helpModal').classList.add('hidden');
    return;
  }
  if (!lbOpen) return;
  if (e.key === 'Escape')                  closeLightbox();
  else if (e.key === 'ArrowLeft')          lbNav(-1);
  else if (e.key === 'ArrowRight')         lbNav(1);
  else if (e.key === 'r' || e.key === 'R') rotate(lb.group.files[lb.idx],  90);
  else if (e.key === 'l' || e.key === 'L') rotate(lb.group.files[lb.idx], -90);
  else if (e.key === '+' || e.key === '=') lbZoomBy(1.5);
  else if (e.key === '-')                  lbZoomBy(1 / 1.5);
  else if (e.key === '0')                  { lbZoom = 1; lbPanX = 0; lbPanY = 0; applyLbRotation(document.getElementById('lb-img')); }
});

// Wheel to zoom in lightbox
document.getElementById('lightbox').addEventListener('wheel', function(e) {
  if (this.classList.contains('hidden')) return;
  e.preventDefault();
  lbZoomBy(e.deltaY < 0 ? 1.12 : 1 / 1.12);
}, { passive: false });

// Drag to pan when zoomed
(function() {
  const lightbox = document.getElementById('lightbox');
  let dragging = false, startX, startY, startPanX, startPanY;
  lightbox.addEventListener('mousedown', function(e) {
    if (lbZoom <= 1 || e.target.tagName === 'BUTTON') return;
    dragging = true;
    startX = e.clientX; startY = e.clientY;
    startPanX = lbPanX; startPanY = lbPanY;
    document.querySelector('.lb-img-wrap').classList.add('dragging');
    e.preventDefault();
  });
  document.addEventListener('mousemove', function(e) {
    if (!dragging) return;
    lbPanX = startPanX + (e.clientX - startX);
    lbPanY = startPanY + (e.clientY - startY);
    applyLbRotation(document.getElementById('lb-img'));
  });
  document.addEventListener('mouseup', function() {
    if (!dragging) return;
    dragging = false;
    document.querySelector('.lb-img-wrap').classList.remove('dragging');
  });
  // Click image to toggle zoom when not dragging
  document.querySelector('.lb-img-wrap').addEventListener('click', function(e) {
    if (e.target.tagName === 'BUTTON') return;
    if (Math.abs(lbPanX - (startPanX || 0)) < 5 && Math.abs(lbPanY - (startPanY || 0)) < 5) {
      lbZoom === 1 ? lbZoomBy(2) : (function(){ lbZoom=1; lbPanX=0; lbPanY=0; applyLbRotation(document.getElementById('lb-img')); })();
    }
  });
})();

// Parse archive data in a Web Worker so the main thread stays responsive
(function() {
  const raw = document.getElementById('archiveData').textContent;
  const blob = new Blob(
    ['onmessage=function(e){postMessage(JSON.parse(e.data));}'],
    {type: 'application/javascript'}
  );
  const workerUrl = URL.createObjectURL(blob);
  const worker = new Worker(workerUrl);
  worker.onmessage = function(e) {
    URL.revokeObjectURL(workerUrl);
    worker.terminate();
    DATA = e.data;

    // Populate year filter
    const years = [...new Set(DATA.map(g => g.date))].sort();
    const sel = document.getElementById('yearFilter');
    years.forEach(y => {
      const o = document.createElement('option');
      o.value = y; o.textContent = y;
      sel.appendChild(o);
    });

    // Initial render
    applyFilters();
    document.getElementById('th-date').className = 'sorted-asc';
  };
  worker.postMessage(raw);
})();
</script>

<div id="helpModal" class="help-modal hidden">
  <div class="help-overlay" onclick="document.getElementById('helpModal').classList.add('hidden')"></div>
  <div class="help-box">
    <header>
      <h2>Farmscape Microfilm Archive &mdash; User Guide</h2>
      <button class="help-close" onclick="document.getElementById('helpModal').classList.add('hidden')" title="Close">&times;</button>
    </header>
    <div class="help-body">

      <h3>Getting Started</h3>
      <p>Images are hosted in the cloud and load automatically &mdash; no setup is required. Simply open the HTML file in your browser and start browsing.</p>
      <div class="tip"><strong>Local folder (optional).</strong> If you have the image files on your own computer, click <strong>Select Images Folder</strong> to load them locally. Local files load faster and work offline. The viewer will use local files when available and fall back to the cloud otherwise.</div>
      <div class="tip" style="margin-top:6px"><strong>The viewer remembers your local folder</strong> between visits. After selecting it once, the button changes to <em>&#8220;&#8617; Re-open &ldquo;[folder name]&rdquo;</em> &mdash; one click restores it. This requires <strong>Chrome or Edge</strong>; Firefox users will need to re-select each visit.</div>

      <h3>Browsing the Table</h3>
      <p>The table lists every academy and year for which files exist, along with the number of images in that group.</p>
      <ul>
        <li><strong>Search box</strong> &mdash; type any part of an academy name or year to filter the table in real time.</li>
        <li><strong>Year dropdown</strong> &mdash; filter to a single year. Works alongside the search box.</li>
        <li><strong>Column headers</strong> &mdash; click <em>Academy</em>, <em>Year</em>, or <em>Files</em> to sort. Click again to reverse the order.</li>
      </ul>

      <h3>Opening a Group</h3>
      <p>Click any row in the table to expand it and see the images for that academy and year. Click the row again to collapse it. Multiple rows can be open at the same time.</p>
      <div class="tip">Images only load when you expand a row, so the page stays fast even with tens of thousands of files.</div>

      <h3>Thumbnail vs List View</h3>
      <p>Use the <strong>Thumbnails</strong> and <strong>List</strong> toggle buttons to switch how images are displayed inside an expanded row.</p>
      <ul>
        <li><strong>Thumbnails</strong> &mdash; a grid of image previews. Best for quickly spotting which images are rotated or identifying content at a glance.</li>
        <li><strong>List</strong> &mdash; a compact list with a small preview and the full filename. Best for finding specific files by name.</li>
      </ul>

      <h3>Viewing a Full-Size Image</h3>
      <p>Click any thumbnail or filename to open the image in the <strong>lightbox viewer</strong>, which overlays the page.</p>
      <ul>
        <li>Use the <strong>Prev</strong> and <strong>Next</strong> buttons to move through all images in the group without closing the viewer.</li>
        <li>Click the dark background or <strong>Close</strong> to return to the table.</li>
      </ul>
      <p>Keyboard shortcuts (when the lightbox is open):</p>
      <ul>
        <li><kbd>&larr;</kbd> <kbd>&rarr;</kbd> &mdash; previous / next image</li>
        <li><kbd>R</kbd> &mdash; rotate clockwise 90&deg;</li>
        <li><kbd>L</kbd> &mdash; rotate counter-clockwise 90&deg;</li>
        <li><kbd>+</kbd> / <kbd>-</kbd> &mdash; zoom in / out</li>
        <li><kbd>0</kbd> &mdash; reset zoom to fit</li>
        <li><kbd>Esc</kbd> &mdash; close the lightbox</li>
      </ul>
      <p><strong>Zooming</strong> &mdash; scroll the mouse wheel to zoom in and out, or use the <strong>+</strong> / <strong>&minus;</strong> buttons in the control bar. Click the image to zoom in; click again to reset. When zoomed in, drag the image to pan around it.</p>

      <h3>Rotating Images</h3>
      <p>Some microfilm scans were filmed sideways and need to be rotated to read correctly.</p>
      <p><strong>Rotate a single image</strong> &mdash; hover over a thumbnail to reveal &#8634; / &#8635; buttons, or use the <strong>&#8634; CCW</strong> / <strong>&#8635; CW</strong> buttons in the lightbox (<kbd>L</kbd> / <kbd>R</kbd> keys also work).</p>
      <p><strong>Rotate a whole group at once</strong> &mdash; use the <strong>&#8634; All</strong> / <strong>&#8635; All</strong> buttons in the lightbox to rotate every image in the current group in one click.</p>
      <p><strong>Rotate a custom selection</strong> &mdash; in thumbnail view, select images first, then use the toolbar that appears above the group:</p>
      <ul>
        <li><kbd>Ctrl</kbd> + click (or <kbd>Cmd</kbd> on Mac) &mdash; toggle individual images in or out of the selection</li>
        <li><kbd>Shift</kbd> + click &mdash; select a range from the last clicked image to this one</li>
        <li><strong>Select All</strong> &mdash; selects every image in the group</li>
        <li><strong>Deselect All</strong> &mdash; clears the selection</li>
        <li><strong>&#8634; Rotate Selected Left / &#8635; Rotate Selected Right</strong> &mdash; rotates only the selected images</li>
      </ul>
      <div class="tip">Rotations are saved instantly to your browser and persist across sessions. A future update will let you export and permanently apply them to the image files.</div>

      <h3>Tips for Large Folders</h3>
      <ul>
        <li>The initial folder scan is done by Windows, not the browser &mdash; it may take 10&ndash;30 seconds before the loading progress begins.</li>
        <li>Images load lazily &mdash; only when you expand a row &mdash; so browsing the table is always fast regardless of how many files are in the folder.</li>
        <li>If the browser seems unresponsive immediately after selecting the folder, it is processing file references in the background. The counter in the status bar will update as it progresses.</li>
      </ul>

    </div>
  </div>
</div>

<div id="lightbox" class="lightbox hidden">
  <div class="lb-overlay" onclick="closeLightbox()"></div>
  <div class="lb-box">
    <div class="lb-img-wrap">
      <img id="lb-img" src="" alt="">
    </div>
    <div class="lb-bar">
      <button class="lb-btn" id="lb-prev" onclick="lbNav(-1)">&#8592; Prev</button>
      <button class="lb-btn" onclick="rotate(lb.group.files[lb.idx], -90)" title="Rotate left (L)">&#8634; CCW</button>
      <button class="lb-btn" onclick="rotate(lb.group.files[lb.idx],  90)" title="Rotate right (R)">&#8635; CW</button>
      <span class="lb-counter" id="lb-counter"></span>
      <button class="lb-btn" onclick="lbZoomBy(1/1.5)" title="Zoom out (-)">&#8722;</button>
      <span class="lb-counter" id="lb-zoom-label" style="min-width:2.8em;text-align:center">1&#xD7;</span>
      <button class="lb-btn" onclick="lbZoomBy(1.5)" title="Zoom in (+)">+</button>
      <button class="lb-btn" id="lb-next" onclick="lbNav(1)">Next &#8594;</button>
      <button class="lb-btn close" onclick="closeLightbox()">&#10005; Close</button>
    </div>
    <div class="lb-label" id="lb-label"></div>
  </div>
</div>
</body>
</html>"""

out_path = os.path.join(base_dir, 'archive_viewer.html')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'Done. Written to: {out_path}')
print(f'{len(data)} groups, {sum(len(g["files"]) for g in data)} files embedded.')
