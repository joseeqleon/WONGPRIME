@echo off
REM Setup Windows Task Scheduler para WongPrime

echo ================================================
echo WongPrime - Configuracion de Tareas Automaticas
echo ================================================
echo.

REM Obtener ruta actual
set CURRENT_DIR=%cd%

echo Creando tarea programada para scraping diario...
schtasks /create /tn "WongPrime_Scraping_Diario" /tr "py %CURRENT_DIR%\run_all_scrapers.py" /sc daily /st 06:00 /f

echo.
echo Creando tarea programada para verificacion de alertas...
schtasks /create /tn "WongPrime_Alertas" /tr "py %CURRENT_DIR%\services\alerts.py" /sc hourly /mo 2 /f

echo.
echo ================================================
echo Tareas programadas creadas exitosamente!
echo ================================================
echo.
echo Tareas creadas:
echo 1. WongPrime_Scraping_Diario - Ejecuta scraping diario a las 6:00 AM
echo 2. WongPrime_Alertas - Verifica alertas cada 2 horas
echo.
echo Puedes ver y administrar las tareas en el Programador de Tareas de Windows
echo.
pause
