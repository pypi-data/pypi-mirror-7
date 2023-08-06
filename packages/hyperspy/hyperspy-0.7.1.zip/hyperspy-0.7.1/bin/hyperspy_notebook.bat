set path=%~dp0;%~dp0\..\;%PATH%
cd %1
python "%~dp0\hyperspy" notebook 
