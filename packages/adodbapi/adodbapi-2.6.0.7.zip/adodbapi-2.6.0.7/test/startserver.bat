rem make a test Jet database
@ECHO On
py setuptestframework.py

rem if "%1%" == "0.0.0.0" goto skip2
rem if "%1%"=="::0" goto skip2
rem start a Pyro4 nameserver and ADO server
start py -m Pyro4.naming --host=0.0.0.0
rem if NOT "%PYRO_HOST%"=="" GOTO skip1
rem if NOT "%1"=="" goto skip0
rem @ECHO 'provide an IP address as the command argument'
rem goto theend
:skip0
py -m adodbapi.server use_nameserver HOST=%1
GOTO theend
:skip1
start py -m adodbapi.server use_nameserver
GOTO theend
:skip2
rem start py -m adodbapi.server HOST=%1
:theend
