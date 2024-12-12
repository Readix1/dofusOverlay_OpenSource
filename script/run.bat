@echo off
set PYTHONPATH=%PYTHONPATH%;.
cd ..
call .\env\Scripts\activate.bat
python main.py --nodebug
pause