@echo off
cd /d D:/Appcation/backend/bosei-meeting-reservation-api/venv1/Scripts
call activate
cd /d D:/Appcation/backend/bosei-meeting-reservation-api
python -m uvicorn app.main:app --host 10.111.170.194