@ECHO OFF
echo  -------------------------------------
echo    remove old .venv
echo  -------------------------------------
DEL .\.venv
echo  -------------------------------------
echo    Create new .venv
echo  -------------------------------------
virtualenv .venv
echo  -------------------------------------
echo    Install required packages
echo  -------------------------------------
call .\.venv\Scripts\activate
call python -m pip install --no-cache-dir -r requirements.txt
pause