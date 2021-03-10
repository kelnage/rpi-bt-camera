ECHO "Compiling Messages.proto into Python and Java output"

:: Move the current working directory to the directory this script is stored in
:: https://serverfault.com/questions/95686/change-current-directory-to-the-batch-file-directory
cd /D "%~dp0"

protoc --python_out=..\server\proto --java_out=..\client\app\src\main\java\pi\raspberry\camera\client\proto Messages.proto

PAUSE