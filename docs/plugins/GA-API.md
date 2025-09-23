# Google Analytics (GA4) Data API – Setup & Usage (Service Account Only)

This guide shows how to pull GA4 metrics directly via the Google Analytics Data API using a Service Account (automation-friendly). We’ll store the JSON key under `.secrets/ga/` (git-ignored) and include a quick smoke test script.

## What you get
- Page-level performance for a date window (example metrics):
  - sessions, totalUsers, engagedSessions, conversions
- Sort and limit the top pages for fast sanity checks.
- Service Account-only setup (no OAuth), suitable for headless runs.

## Quickstart (Exact names/paths for this project)

- Recommended Google Cloud Project: `EllieEdwardsMarketing-GA-API` (you can reuse the GSC project if you prefer)
- Service account name: `seolab-ga-api-sa`
- GA4 Property ID: `500316527`
- Local secrets folder: `C:\Users\rhode\source\repos\seolab\.secrets\ga\`
  - Key file path: `C:\Users\rhode\source\repos\seolab\.secrets\ga\service_account.json`
- Scope: `https://www.googleapis.com/auth/analytics.readonly`
- API: Google Analytics Data API (enable in Cloud Console)

> Note: The `.secrets/` folder is already git-ignored in this repo.

---

### Finding your GA4 Property ID

You’ll grab this from the Google Analytics interface (not from Tag Manager):

1) Open Google Analytics (analytics.google.com) and select the correct property.
2) Click the gear icon (Admin) in the lower-left corner.
3) In the Property column, click “Property settings”.
4) Look for “Property ID” — it’s a numeric value like `123456789`.

Notes:
- Don’t confuse the Property ID with the Measurement ID (which looks like `G-XXXXXXXX`). The smoke test needs the numeric Property ID.
- If you don’t see the property, ask for access or create a GA4 property first, then add the service account email as a user at the property level.

---

## Step-by-step (Service Account)

1) Create the service account (Cloud Console)
- Google Cloud Console → IAM & Admin → Service Accounts → Create Service Account
  - Service account name: `seolab-ga-api-sa` (matches your screenshot)
  - Service account ID: auto-filled to `seolab-ga-api-sa` (keep default)
  - Description: `Service account for seolab GA4 Data API access`
  - Create and Continue → you can skip adding roles here (GA access is managed in GA Admin). Done.

2) Create and download a JSON key
- Open the service account → Keys → Add key → Create new key → JSON
- Save to: `C:\Users\rhode\source\repos\seolab\.secrets\ga\service_account.json`
 - If the folder doesn't exist yet:
```powershell
New-Item -ItemType Directory -Force -Path C:\Users\rhode\source\repos\seolab\.secrets\ga | Out-Null
```

3) Enable the API
- In Cloud Console → APIs & Services → Library → search for "Google Analytics Data API" → Enable.

4) Grant access in Google Analytics (critical)
- GA Admin → Property access management (for your GA4 property ID)
- Add user → Email = `seolab-ga-api-sa@<project-id>.iam.gserviceaccount.com` (copy the exact email from the service account)
- Role: Viewer (or Analyst) is sufficient for read access.

5) Install Python deps (if not already)
```powershell
& C:\Users\rhode\source\repos\seolab\.venv\Scripts\Activate.ps1
pip install google-analytics-data google-auth
```

Troubleshooting deps (Streamlit envs):
```powershell
# If Streamlit complains about protobuf version, pin it below 6
pip install "protobuf<6"
```

6) Smoke test (page-level top pages)
- A small script lives at `tools/ga_service_smoke.py`. It prints top pages for the last N days.
- Usage (PowerShell):
```powershell
& C:\Users\rhode\source\repos\seolab\.venv\Scripts\Activate.ps1
python tools/ga_service_smoke.py --property-id 500316527 --days 28 --row-limit 25
```

### What the smoke test does
- Authenticates using the Service Account key at `.secrets/ga/service_account.json`.
- Queries GA4 Data API `runReport` with dimensions `[pagePath]` and metrics `[sessions,totalUsers,engagedSessions,conversions]`.
- Date window: last N days, ending 2 days ago (to avoid GA4 processing lag).
- Orders by `sessions` desc and prints the rows as JSON.

---

## Tips & Notes
- Finding your GA4 Property ID: GA Admin → Property Settings → Property ID (a number like 123456789).
- Freshness: GA4 can lag a bit; using a window that ends 2 days ago gives more stable numbers.
- Permissions: If you get a 403/permission error, ensure the service account email is added at the property level.
- Multiple properties: You can run the smoke test against any property by changing `--property-id`.
- Next: We can add a Streamlit test page and a plugin wrapper to feed GA metrics into the orchestrator.
