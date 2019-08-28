
****************************************************
Codechat Plugin
****************************************************
The CodeChat plugin transforms source code into a web page, allowing software developers to view their source code as a beautiful and descriptive document by adding headings, formatting, hyperlinks, images, and diagrams.

Getting Started
==================
This project proposes the creation of a modular plug-in architecture for CodeChat, enabling its use with Visual Studio Code. A significant challenge to creating a modular plug-in involves bridging the services CodeChat provides, which are defined in the Python programming language, to the variety of programming languages which various text editors require. To accomplish this, this project employs Apache Thrift, which provides scalable cross-language service development. By describing the services CodeChat provides in a language-neutral format (a .thrift file), Apache Thrift can then generate code for a wide variety of different programming languages. Next, this project proposes development of a CodeChat server to provide the needed services and the creation of a JavaScript plugin client for Visual Studio Code (VSCode), a free and popular cross-platform text editor. After creating the plugin for VSCode, our next approach will be to develop plugins for other editors such as Visual Studio, Atom and Sublime. These editors employ different languages, so our work will only consist of providing the necessary interface between the CodeChat server and a supported language plugin client for the editor.

The plugin architecture is shown in the `Codechat Plugin Architecture.png <https://github.com/mrsuman2002/A_modular_Plugin-CodeChat/blob/master/Codechat%20Plugin%20Architecture.png>`_

Prerequisites:
===============
- Installation of python
    make sure you have installed python 3
- Installation of Node.js
- Installation of npm

There are two location from where all the installation should be done from
1. CodeChat_extension location (see the documentation at Codechat_Extension/CodeChat_Extension_Readme.rst )

    C:\Users\suman\Desktop\MSU_Spring_2018\Research\A_modular_Plugin-CodeChat\CodeChat_Extension>npm install
    
2. Python_Server location (see the documentation at thrift/Python_Server/Python_Server_Readme.rst)
    C:\Users\suman\Desktop\MSU_Spring_2018\Research\A_modular_Plugin-CodeChat\Thrift\Python_Server>pip install Codechat

    C:\Users\suman\Desktop\MSU_Spring_2018\Research\A_modular_Plugin-CodeChat\Thrift\Python_Server>pip install thrift
    
    C:\Users\suman\Desktop\MSU_Spring_2018\Research\A_modular_Plugin-CodeChat\Thrift\Python_Server>pip install -U flask-cors



Built with:
=============
Yoeman Generator

License:
===========
Copyright Copyright (C) 2012-2018 Bryan A. Jones.

This file is part of CodeChat Plugin.

CodeChat Plugin is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

CodeChat Plugin is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received `a copy of the GNU General Public License <https://github.com/mrsuman2002/A_modular_Plugin-CodeChat/blob/master/LICENSE.rst>`_ along with CodeChat. If not, see http://www.gnu.org/licenses/.
