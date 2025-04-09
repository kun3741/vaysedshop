@echo off

IF NOT EXIST "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat


cd vaysedshop-main

echo Installing libraries...
pip install pillow, Django


echo Applying migrations...
python manage.py migrate

echo Starting Django server...
python manage.py runserver

pause
