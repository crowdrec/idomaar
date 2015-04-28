@echo off
if "%~1"=="" (
  echo "Specify recommendation engine address: http://<host>:port."
  exit /B 1
)
set basedir=%~dp0
%basedir%/../idomaar.bat --comp-env-address %1 --data-source newsreel-test/2014-07-01.data.idomaar_1k.txt --newsreel --new-topic