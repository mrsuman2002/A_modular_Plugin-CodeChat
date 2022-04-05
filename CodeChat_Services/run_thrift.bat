REM .. Copyright (C) 2012-2022 Bryan A. Jones.
REM
REM     This file is part of the CodeChat System.
REM
REM     The CodeChat System is free software: you can redistribute it and/or
REM     modify it under the terms of the GNU General Public License as
REM     published by the Free Software Foundation, either version 3 of the
REM     License, or (at your option) any later version.
REM
REM     The CodeChat System is distributed in the hope that it will be
REM     useful, but WITHOUT ANY WARRANTY; without even the implied warranty
REM     of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
REM     General Public License for more details.
REM
REM     You should have received a copy of the GNU General Public License
REM     along with the CodeChat System.  If not, see
REM     <http://www.gnu.org/licenses/>.
REM
REM ***************************************************
REM |docname| - Build interface files from Thift source
REM ***************************************************
REM This requires the `Apache Thrift compiler <https://thrift.apache.org/download>`_.

mkdir ..\CodeChat_Server\CodeChat_Server\gen_py
thrift-0.16.0.exe --gen py --strict -out ..\CodeChat_Server\CodeChat_Server\gen_py CodeChat_Services.thrift
thrift-0.16.0.exe --gen js:node,ts --strict -o ..\extensions\VSCode\src CodeChat_Services.thrift
