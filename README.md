# New York Academy Meteorological Observations
### Farmscape Weather Data — Microfilm Archive

A browsable archive of handwritten meteorological observation reports submitted by New York State academies to the Regents of the University of the State of New York, covering the years **1827–1860**.

---

## Browse the Archive

**[Open the viewer →](https://markleyboyer.github.io/microfilm-archive/)**

No installation required. The viewer runs entirely in your browser. Images are served from the cloud and load automatically.

---

## The Collection

| | |
|---|---|
| **Period covered** | 1827–1860 (plus a 1850–1860 grouped set) |
| **Total images** | 25,638 JPG files |
| **Unique academy/year groups** | 1,026 |
| **Academies represented** | ~90 institutions across New York State |

Reports were submitted annually by academies participating in the Regents program. Each file contains handwritten weather observations recorded by academy instructors — temperature, precipitation, wind, and general conditions — representing one of the earliest systematic meteorological datasets in the United States.

### File Naming Convention

All image files follow this pattern:

```
IMG_XXXX_YYYYAcademyName.JPG
```

- `IMG_XXXX` — sequential scan number
- `YYYY` — year of the report (e.g. `1829`)
- `AcademyName` — institution name in CamelCase (e.g. `FairfieldAcademy`)

Some groups span a date range (e.g. `1850-1860HomerAcademy`).

---

## Using the Viewer

- **Search** by academy name or year using the search box
- **Filter** to a single year using the dropdown
- **Sort** by clicking any column header
- **Click a row** to expand it and view the images for that group
- **Click any image** to open the full-size lightbox viewer
- **Rotate images** using the ↺ ↻ buttons — corrections are saved automatically
- **Keyboard shortcuts** in the lightbox: `←` `→` to navigate, `R`/`L` to rotate, `Esc` to close
- Click **?** in the toolbar for the full user guide

---

## Repository Contents

| File | Description |
|---|---|
| `index.html` | The self-contained archive viewer (browse without cloning) |
| `build_viewer.py` | Python script that regenerates `index.html` from the images folder |
| `analyze_filenames.py` | Utility script to audit filenames and generate a summary report |
| `report.csv` | Summary table of all academy/year groups and file counts |
| `UPDATING.md` | Guide for adding new images and regenerating the viewer |

---

## Technical Stack

- **Viewer** — single self-contained HTML file with embedded JSON index, vanilla JavaScript, no dependencies
- **Images** — hosted on [Cloudflare R2](https://developers.cloudflare.com/r2/) object storage (~$0.54/month, free egress)
- **Hosting** — [GitHub Pages](https://pages.github.com/) (free)
- **Image processing** — Python with Pillow (planned: thumbnail generation, rotation export)

---

## Planned Features

- [ ] Generate small thumbnails for faster cloud browsing
- [ ] Export rotation corrections as a permanent fix to image files
- [ ] AI transcription pipeline for handwritten text extraction
