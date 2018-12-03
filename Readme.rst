
****************************************************
Codechat Plugin
****************************************************
The CodeChat plugin transforms source code into a web page, allowing software developers to view their source code as a beautiful and descriptive document by adding headings, formatting, hyperlinks, images, and diagrams.

Getting Started
==================
This project proposes the creation of a modular plug-in architecture for CodeChat, enabling its use with Visual Studio Code. A significant challenge to creating a modular plug-in involves bridging the services CodeChat provides, which are defined in the Python programming language, to the variety of programming languages which various text editors require. To accomplish this, this project employs Apache Thrift, which provides scalable cross-language service development. By describing the services CodeChat provides in a language-neutral format (a .thrift file), Apache Thrift can then generate code for a wide variety of different programming languages. Next, this project proposes development of a CodeChat server to provide the needed services and the creation of a JavaScript plugin client for Visual Studio Code (VSCode), a free and popular cross-platform text editor. After creating the plugin for VSCode, our next approach will be to develop plugins for other editors such as Visual Studio, Atom and Sublime. These editors employ different languages, so our work will only consist of providing the necessary interface between the CodeChat server and a supported language plugin client for the editor.

The plugin architecture is shown in the Codechat Plugin Architecture.jpg https://github.com/mrsuman2002/A_modular_Plugin-CodeChat/blob/master/CodeChat%20Plugin%20Architecture.jpg

# Prerequisites:
=============
- Installation of python
- Installation of Node.js
- Installation of npm
- Installation of thrift

# Deployment:


# Built with:
Yoeman Generator

# License:
This is an open source non commerce plugin for VSCode.
