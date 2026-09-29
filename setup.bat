@echo off
echo Setting up Python environment...
python -m venv .venv
call .venv\Scripts\activate
pip install -r requirements.txt
echo Setup completed!
pause
