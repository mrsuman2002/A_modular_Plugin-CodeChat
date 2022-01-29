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
REM ******************************************************
REM |docname| - Run the Sphinx build from the command line
REM ******************************************************
REM Below is an easy way to include additional builders in the build.
REM PATH = %PATH%;c:\Program Files\doxygen\bin;c:\Program Files\Java\jdk-16.0.2\bin
sphinx-build -d _build\doctrees . _build
