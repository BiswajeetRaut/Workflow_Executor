# Workflow_Executor

Terraform / GitHub / Confluence workflow automation builder with graph-based execution.

## Local run

### Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

### Frontend
```bash
cd workflow_ui
npm install
npm run dev
```

## Pre-merge sanity check (recommended)

If you resolved conflicts manually (especially with "Accept both"), run:

```bash
python backend/scripts/premerge_sanity.py
```

This validates:
- no leftover merge markers (`<<<<<<<`, `=======`, `>>>>>>>`)
- backend Python files still compile
