@echo off
if "%~2"=="" (
	echo "usage: newsreel.bat <recommendation-engine-address> <data-source>"
    echo "e.g. newsreel.bat http://host:port path/to/data/file"
    echo "Use forward slashes (/) as the directory separator."
    exit /B 1
)
set basedir=%~dp0
%basedir%/../idomaar.bat --comp-env-address %1 --data-source %2 --newsreel --new-topic