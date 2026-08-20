$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root\backend'; py -3 main.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root'; py -3 -m http.server 5175 --directory frontend"
Write-Host "Backend: http://localhost:8000"
Write-Host "Frontend: http://localhost:5175"