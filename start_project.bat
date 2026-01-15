@echo off
echo ================================================
echo WongPrime - Iniciando Proyecto Completo
echo ================================================
echo.

echo [1/3] Iniciando API REST (FastAPI)...
start "WongPrime API" cmd /k "py -m api.main"

timeout /t 3 /nobreak > nul

echo [2/3] Abriendo Documentación API...
start http://localhost:8000/docs

echo [3/3] Abriendo Dashboard...
start dashboard\index.html

echo.
echo ================================================
echo Proyecto WongPrime iniciado correctamente!
echo ================================================
echo.
echo Servicios activos:
echo - API REST: http://localhost:8000
echo - API Docs: http://localhost:8000/docs
echo - Dashboard: dashboard\index.html
echo.
echo Presiona cualquier tecla para finalizar...
pause > nul
