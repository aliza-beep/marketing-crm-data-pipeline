$ErrorActionPreference = "Stop"
if (-not (Test-Path ".env")) { Copy-Item ".env.example" ".env" }
python -m marketing_pipeline.pipeline --days 30
python -m marketing_pipeline.export
python -m marketing_pipeline.ai.diagnostics --no-ai
Write-Host "Data, Power BI exports, and local diagnostic report are ready."
Write-Host "Start dashboard: streamlit run src/marketing_pipeline/dashboard/app.py"

