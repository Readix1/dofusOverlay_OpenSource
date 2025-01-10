@echo off
set PYTHONPATH=%PYTHONPATH%;.
cd ..
call .\.env\Scripts\activate.bat
python dofusOverlay3.py --nodebug
pause