@echo off
cd C:\Users\samli\Desktop\worldcup_api
call venv\Scripts\activate
python scripts/run_agent.py --task scrape_daily --date %DATE:~0,4%-%DATE:~5,2%-%DATE:~8,2%