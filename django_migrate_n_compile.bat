@ECHO OFF
echo.
echo  -------------------------------------
echo    Apply Migrations
echo  -------------------------------------
echo.
call .\.venv\Scripts\activate
call python manage.py migrate
echo.
echo  -------------------------------------
echo    Handle Translations
echo  -------------------------------------
echo.
call django-admin compilemessages -l de
echo.
echo  -------------------------------------
echo    Collect static files
echo  -------------------------------------
echo.
call python manage.py collectstatic
pause
