set path=%~dp0;%~dp0\..\;%PATH%
cd %1
start pythonw "%~dp0\hyperspy " qtconsole 
