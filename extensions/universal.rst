*****************************
Universal extensions/plug-ins
*****************************
The CodeChat Server offers two modes that will work with almost any text editor or IDE:

-   A `file change watcher <CodeChat_Server-watch>` which renders any file as soon as it's saved. For example, executing ``CodeChat_Server watch`` will monitor all files in the current directory and all it subdirectories for a change, rendering as soon as the change is detected. This command can be run multiple times from multiple directories.

-   A `command-line render option <CodeChat_Server-render>` that allows an editor or IDE to perform a render by executing the CodeChat server with the ``render`` subcommand. This is useful for editors like VIM: use ``:nmap <C-X> :w<cr>:!CodeChat_Server render % 1<CR>`` to define the Ctrl-X command which saves the current file and renders it. If you'd like to render files in a separate window, replace the ``1`` with any other number of your choice.
