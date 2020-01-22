REM ***************************************************
REM |docname| - Build interface files from Thift source
REM ***************************************************
REM This requires the `Apache Thrift compiler <https://thrift.apache.org/download>`_.

thrift-0.13.0.exe --gen py --gen js --strict -o ..\CodeChat_Server CodeChat_Services.thrift
thrift-0.13.0.exe --gen js:node --strict -o ..\VSCode_Extension CodeChat_Services.thrift
