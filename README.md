# AI-Railway-Safety-System

## Run the combined system

From PowerShell:

```powershell
Set-Location .
.\run-process.ps1
```

Open the dashboard at `http://localhost:5175/`. It reads live data from the FastAPI backend at `http://localhost:8000/api/v1`.

To run the services separately:

```powershell
Set-Location .\backend
py -3 main.py

# In another terminal
Set-Location .
py -3 -m http.server 5175 --directory frontend
```