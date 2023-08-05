rem make a test folder for python 3.0 to 3.2
mkdir ..\3test
copy *.bat ..\3test\*.*
py C:\Python27\Tools\Scripts\2to3.py . -n -w -W --output-dir=..\3test
cd ..\3test
