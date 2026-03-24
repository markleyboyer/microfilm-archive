# Updating the Archive

This guide covers how to add new images, regenerate the viewer, and push updates online.

---

## Prerequisites

- **Python 3** — to run the build scripts
- **rclone** — to upload images to Cloudflare R2 (`winget install Rclone.Rclone`)
- **rclone configured** — see the R2 configuration section below

---

## Adding New Images

### 1. Name the files correctly

All image files must follow this naming convention:

```
IMG_XXXX_YYYYAcademyName.JPG
```

- `IMG_XXXX` — any sequential number
- `YYYY` — four-digit year (or range like `1850-1860`)
- `AcademyName` — institution name in CamelCase, no spaces

Examples:
```
IMG_0001_1829FairfieldAcademy.JPG
IMG_0002_1829FairfieldAcademy.JPG
IMG_0001_1850-1860HomerAcademy.JPG
```

### 2. Place files in the images folder

Copy the new JPG files into:
```
images\
```

### 3. Regenerate the viewer

From the project folder, run:

```powershell
python build_viewer.py
```

This scans the `images\` folder, rebuilds the JSON index, and writes a new `archive_viewer.html`.

### 4. Upload new images to Cloudflare R2

```powershell
rclone copy "images" r2:meteorologicalobservations/images --progress --transfers 8
```

rclone skips files already uploaded — only new files are transferred.

### 5. Upload the updated viewer to GitHub

```powershell
python push_to_github.py
```

Or upload `archive_viewer.html` manually to GitHub as `index.html`:
1. Go to [github.com/markleyboyer/microfilm-archive](https://github.com/markleyboyer/microfilm-archive)
2. Click `index.html` → the pencil (edit) icon
3. Select all, paste the new content, commit

The live site updates within 1–2 minutes.

---

## Checking for Filename Issues

To audit the `images\` folder for unusual or malformed filenames:

```powershell
python analyze_filenames.py images
```

This prints a summary table and saves a report to `unique_names_report.txt`.

---

## Rclone Configuration

The rclone config file lives at:
```
C:\Users\<you>\.config\rclone\rclone.conf
```

It should contain:

```ini
[r2]
type = s3
provider = Cloudflare
access_key_id = <your R2 access key>
secret_access_key = <your R2 secret key>
endpoint = https://ddc9cb01a6eac4e03b754274e317a865.r2.cloudflarestorage.com
acl = private
```

To get new R2 credentials:
1. Go to the [Cloudflare dashboard](https://dash.cloudflare.com)
2. R2 Object Storage → Manage R2 API Tokens
3. Create Account API Token with Object Read & Write permission

---

## Cloudflare R2 Details

| | |
|---|---|
| **Bucket** | `meteorologicalobservations` |
| **Public URL** | `https://pub-e96a83f726634e6a8bac05a0641d11fe.r2.dev` |
| **Images path** | `/images/` |
| **Estimated cost** | ~$0.54/month storage, free egress |

---

## GitHub Pages Details

| | |
|---|---|
| **Repository** | [github.com/markleyboyer/microfilm-archive](https://github.com/markleyboyer/microfilm-archive) |
| **Live URL** | [markleyboyer.github.io/microfilm-archive](https://markleyboyer.github.io/microfilm-archive/) |
| **Branch** | `main` |
| **Source file** | `index.html` |
