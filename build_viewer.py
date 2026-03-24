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
  table { width: 100%; border-collapse: collapse; }
  thead th { background: #3d3020; color: #f5f0e8; padding: 11px 16px; text-align: left; font-size: 0.8rem; letter-spacing: 0.08em; text-transform: uppercase; font-weight: normal; cursor: pointer; user-select: none; }
  thead th:hover { background: #52432e; }
  thead th.sorted-asc::after { content: " \u25b2"; }
  thead th.sorted-desc::after { content: " \u25bc"; }
  tbody tr.group-row { cursor: pointer; border-bottom: 1px solid #ddd6c4; transition: background 0.1s; }
  tbody tr.group-row:hover { background: #ede8dc; }
  tbody tr.group-row.expanded { background: #e5dfc9; }
  tbody tr.group-row td { padding: 10px 16px; font-size: 0.92rem; }
  td.count { text-align: right; color: #6b5e45; font-size: 0.85rem; }
  td.date-col { font-variant-numeric: tabular-nums; color: #4a3c28; }
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
  /* Lightbox */
  .lightbox { position: fixed; inset: 0; z-index: 1000; display: flex; align-items: center; justify-content: center; }
  .lightbox.hidden { display: none; }
  .lb-overlay { position: absolute; inset: 0; background: rgba(0,0,0,0.88); }
  .lb-box { position: relative; z-index: 1; display: flex; flex-direction: column; align-items: center; gap: 10px; }
  .lb-img-wrap { display: flex; align-items: center; justify-content: center; width: 90vw; height: 80vh; overflow: hidden; }
  .lb-img-wrap img { max-width: 90vw; max-height: 80vh; object-fit: contain; transform-origin: center; transition: transform 0.25s; }
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
  <button class="help-btn" onclick="document.getElementById('helpModal').classList.remove('hidden')" title="User guide">?</button>
</div>
<table id="mainTable">
  <thead>
    <tr>
      <th style="width:28px;cursor:default"></th>
      <th onclick="sortBy('name')" id="th-name">Academy</th>
      <th onclick="sortBy('date')" id="th-date">Year</th>
      <th onclick="sortBy('count')" id="th-count" style="text-align:right">Files</th>
    </tr>
  </thead>
  <tbody id="tbody"></tbody>
</table>
<div id="noResults" class="no-results" style="display:none">No matching records found.</div>

<script>
const DATA = """ + data_json + """;
const R2_BASE = 'https://pub-e96a83f726634e6a8bac05a0641d11fe.r2.dev/images/';

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

// Populate year filter
const years = [...new Set(DATA.map(g => g.date))].sort();
const sel = document.getElementById('yearFilter');
years.forEach(y => {
  const o = document.createElement('option');
  o.value = y; o.textContent = y;
  sel.appendChild(o);
});

function fileUrl(fname) {
  return fileMap[fname] || R2_BASE + encodeURIComponent(fname);
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

  rows.forEach(g => {
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

    tbody.appendChild(tr);
    tbody.appendChild(filesRow);
  });
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
    const wrap = document.createElement('div');
    wrap.className = 'thumbnails';
    g.files.forEach((f, idx) => {
      const url   = fileUrl(f);
      const label = f.replace(/^IMG_\\d+ ?(\\(\\d+\\))?_/, '').replace('.JPG', '');

      const item = document.createElement('div');
      item.className = 'thumb-item';

      // Image wrapper — click opens lightbox
      const imgWrap = document.createElement('div');
      imgWrap.className = 'thumb-img-wrap';
      imgWrap.addEventListener('click', () => openLightbox(g, idx));

      const img = document.createElement('img');
      img.src = url;
      img.loading = 'lazy';
      img.dataset.fname = f;
      img.alt = f;
      applyImgRotation(img);

      const btns = document.createElement('div');
      btns.className = 'thumb-btns';
      btns.appendChild(makeRotBtn('\\u21ba', 'Rotate left', f, -90));
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
      img.src = url;
      img.loading = 'lazy';
      img.dataset.fname = f;
      img.alt = f;
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

// Rotation state — persisted in localStorage
const rotations = JSON.parse(localStorage.getItem('microfilm_rotations') || '{}');

function getRotation(fname) { return rotations[fname] || 0; }

function rotate(fname, delta) {
  rotations[fname] = ((getRotation(fname) + delta) + 360) % 360;
  localStorage.setItem('microfilm_rotations', JSON.stringify(rotations));
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

function applyLbRotation(img) {
  const deg = getRotation(img.dataset.fname);
  const swap = deg === 90 || deg === 270;
  // Swap max constraints so rotated image still fits the viewport
  img.style.maxWidth  = swap ? '80vh' : '90vw';
  img.style.maxHeight = swap ? '90vw' : '80vh';
  img.style.transform = 'rotate(' + deg + 'deg)';
}

// Lightbox
const lb = { group: null, idx: 0 };

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
  const f   = lb.group.files[lb.idx];
  const img = document.getElementById('lb-img');
  img.src            = fileMap[f] || '';
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
});

// Initial render
applyFilters();
document.getElementById('th-date').className = 'sorted-asc';
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
        <li><kbd>Esc</kbd> &mdash; close the lightbox</li>
      </ul>

      <h3>Rotating Images</h3>
      <p>Some microfilm scans were filmed sideways and need to be rotated to read correctly. You can correct these in two ways:</p>
      <ul>
        <li><strong>In thumbnail view</strong> &mdash; hover over a thumbnail to reveal <strong>&#8634;</strong> (rotate left) and <strong>&#8635;</strong> (rotate right) buttons.</li>
        <li><strong>In the lightbox</strong> &mdash; use the <strong>&#8634; CCW</strong> and <strong>&#8635; CW</strong> buttons in the control bar, or the <kbd>L</kbd> / <kbd>R</kbd> keys.</li>
      </ul>
      <div class="tip"><strong>Tip:</strong> If all images in a group are rotated the same way, open the lightbox on the first image, press <kbd>R</kbd> or <kbd>L</kbd> to correct it, then use <kbd>&rarr;</kbd> to advance and repeat. Rotations are saved instantly and will still be applied the next time you open the viewer.</div>
      <p>Rotation corrections are stored in your browser&rsquo;s local storage (tied to this HTML file on this computer). They persist across sessions but are not shared with others. A future version will allow you to export and apply these corrections as a permanent fix to the image files.</p>

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
