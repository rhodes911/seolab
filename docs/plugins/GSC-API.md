# Google Search Console API – Setup & Usage (Service Account Only)

This guide shows how to connect directly to your GSC property using a Service Account (recommended for automation and headless use). It uses a JSON key stored locally under `.secrets/gsc/` (git-ignored).

## What you get
- Live GSC metrics per keyword: impressions, clicks, CTR, position.
- Normalized fields for enrichment (e.g., quick-win flags).

## Prerequisites
- You (or your org) control the GSC property (Domain property recommended).
- You can add a user to the property in Search Console.
- Python deps installed in your venv: `google-api-python-client`, `google-auth`.

## Quickstart (Exact names for this project)

- Google Cloud Project: `EllieEdwardsMarketing-GSC-API`
- Service account name: `seolab-gsc-api-sa`
- GSC property (siteUrl): `sc-domain:ellieedwardsmarketing.com`
- Local secrets folder: `C:\Users\rhode\source\repos\seolab\.secrets\gsc\`
  - Service account key: `C:\Users\rhode\source\repos\seolab\.secrets\gsc\service_account.json`
- Scope: `https://www.googleapis.com/auth/webmasters.readonly`

> The `.secrets/` folder is git-ignored in this repo.

---

## Step-by-step (Service Account)

1) Create the service account (Cloud Console)
- Google Cloud Console → IAM & Admin → Service Accounts → Create Service Account
  - Service account name: `seolab-gsc-api-sa`
  - Service account ID: auto-fills (keep default)
  - Description: `Service account for seolab GSC API access`
  - Click Create and Continue
  - Roles: you can skip assigning roles (Search Console access is granted in GSC UI). Continue → Done

2) Create and download a JSON key
- Open the service account you just created → Keys → Add key → Create new key → JSON
- Save to: `C:\Users\rhode\source\repos\seolab\.secrets\gsc\service_account.json`
- Ensure the `.secrets` folder exists (it is git-ignored).

3) Grant access in Search Console (critical)
- Open Search Console → select property `sc-domain:ellieedwardsmarketing.com`
- Settings → Users and permissions → Add user
- Email: `seolab-gsc-api-sa@<project-id>.iam.gserviceaccount.com` (copy from the SA details)
- Permission: Full (recommended) or Restricted
- Save

4) Install Python deps (if not already)
```powershell
& C:\Users\rhode\source\repos\seolab\.venv\Scripts\Activate.ps1
pip install google-api-python-client google-auth
```

5) Smoke test (Service Account)
- Save as `C:\Users\rhode\source\repos\seolab\tools\gsc_service_smoke.py`:
- Once working, we’ll wire this into a `gsc_api` plugin and an orchestrator step to enrich keyword lists with live GSC metrics (impressions, clicks, CTR, position) and quick-win flags.
```python
import json, datetime as dt
from googleapiclient.discovery import build
  - Service account ID: auto-fills (keep default)
