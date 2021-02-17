// .. Copyright (C) 2012-2020 Bryan A. Jones.
//
//  This file is part of the CodeChat system.
//
//  The CodeChat system is free software: you can redistribute it and/or
//  modify it under the terms of the GNU General Public License as
//  published by the Free Software Foundation, either version 3 of the
//  License, or (at your option) any later version.
//
//  The CodeChat system is distributed in the hope that it will be
//  useful, but WITHOUT ANY WARRANTY; without even the implied warranty
//  of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
//  General Public License for more details.
//
//  You should have received a copy of the GNU General Public License
//  along with the CodeChat system.  If not, see
//  <http://www.gnu.org/licenses/>.
//
// *****************************************************
// |docname| - The CodeChat Visual Studio Code extension
// *****************************************************
// This extension creates a webview (see `activation/deactivation`_), then uses `CodeChat services`_ to render editor text in that webview.
//
// Terminology:
//
// -    The ``connection`` is a Thrift network connection to the CodeChat server.
// -    The ``client`` is the Thrift client using that network connection.
// -    The render client (identified by a unique ``id``) is obtained using the ``client``, and can be used to render code to HTML.
//
//
// Requirements
// ============
// Node.js packages
// ----------------
import assert = require('assert');
import child_process = require('child_process');

// Third-party packages
// --------------------
import escape = require('escape-html');
import shlex = require('shlex');
import thrift = require('thrift');
import vscode = require('vscode');

// Local packages
// --------------
import EditorPlugin = require('./gen-nodejs/EditorPlugin');
import ttypes = require('./gen-nodejs/CodeChat_Services_types');

// Globals
// =======
// These globals are truly global: only one is needed for this entire plugin.
//
// The Thrift network connection to the CodeChat server.
let connection: thrift.Connection | undefined = undefined;
// The Thrift client using this connection.
let client: EditorPlugin.Client | undefined = undefined;
// Where the webclient resides: ``html`` for a webview panel embedded in VSCode; ``browser`` to use an external browser.
const client_location: ttypes.CodeChatClientLocation = ttypes.CodeChatClientLocation.html;
// The subprocess in which the CodeChat server runs.
let codechat_server: {
    run_server: () => void,
    is_server_running: () => boolean,
    terminal: vscode.Terminal
} | undefined = undefined;

// A unique instance of these variables is required for each CodeChat panel. However, this code doesn't have a good UI way to deal with multiple panels, so only one is supported at this time.
//
// The id of this render client, assigned by the CodeChat server.
let id: number | undefined = undefined;
// The webview panel used to display the CodeChat client
let panel: vscode.WebviewPanel | undefined = undefined;
// A timer used to wait for additional events (keystrokes, etc.) before performing a render.
let idle_timer: NodeJS.Timeout | undefined = undefined;


// Activation/deactivation
// =======================
// This is invoked when the extension is activated. It either creates a new CodeChat instance or reveals the currently running one.
export function activate(context: vscode.ExtensionContext) {
    context.subscriptions.push(vscode.commands.registerCommand('extension.codeChat', () => {

        // Create or reveal the webview panel.
        if (client_location === ttypes.CodeChatClientLocation.html) {
            if (panel !== undefined) {
                // As below, don't take the focus when revealing.
                panel.reveal(undefined, true);
            } else {
                // Create a webview panel.
                panel = vscode.window.createWebviewPanel(
                    "CodeChat", "CodeChat",
                    {
                        // Without this, the focus becomes this webview; seeting this allows the code window open before this command was executed to retain the focus and be immediately rendered.
                        preserveFocus: true,
                        // Put this in the a column beside the current column.
                        viewColumn: vscode.ViewColumn.Beside,
                    },
                    {
                        enableScripts: true,
                    }
                );
                context.subscriptions.push(panel.onDidDispose( (event) => {
                    // Shut down the render client when the webview panel closes.
                    stop_client();
                    panel = undefined;
                }));
            }
        } else {
            // Provide a way to restart the client in the external browser.
            stop_client();
        }

        // Provide a simple status display while the CodeChat system is starting up.
        if (panel !== undefined) {
            // If we have an ID, then the GUI is already running; don't replace it.
            if (id === undefined) {
                panel.webview.html = "<h1>CodeChat</h1><p>Loading...</p>";
            }
        } else {
            vscode.window.showInformationMessage("CodeChat is loading in an external browser...");
        }

        if (codechat_server === undefined) {
            // Create the CodeChat Server terminal if it doesn't exist; this also runs its when the terminal is ready.
            create_CodeChat_terminal();
        } else {
            // Run the CodeChat server if it's not currently running; we assume the terminal is ready.
            codechat_server.run_server();
        }

        // Show the terminal, in case there are errors. This helps the user understand what's going wrong.
        assert(codechat_server !== undefined);
        codechat_server.terminal.show(true);

        if (connection === undefined) {
            // The client should never exist if there's no connection.
            assert(client === undefined);

            // Try to connect to the CodeChat server. The `createConnection function <https://github.com/apache/thrift/blob/master/lib/nodejs/lib/thrift/connection.js#L258>`_ wraps `net.createConnection <https://nodejs.org/api/net.html#net_net_createconnection_options_connectlistener>`_ then returns a `Connection object <https://github.com/apache/thrift/blob/master/lib/nodejs/lib/thrift/connection.js#L35>`_.
            //
            // This must use the `CodeChat service port <CodeChat service port>`.
            connection = thrift.createConnection("localhost", 9090, {
                transport: thrift.TBufferedTransport,
                protocol:  thrift.TBinaryProtocol,
                connect_timeout: 10,
                timeout: 10,
            });

            let was_error: boolean = false;

            connection.on('error', function(err) {
                was_error = true;
                show_error(`Error communicating with the CodeChat server: ${err.message}. Re-run the CodeChat extension to restart it.`);
                // The close event will be `emitted next <https://nodejs.org/api/net.html#net_event_error_1>`_; that will handle cleanup.
            });

            connection.on('close', (hadError) => {
                // If there was an error, the event handler above already provided the message. Note: the `parameter hadError <https://nodejs.org/api/net.html#net_event_close_1>`_ doesn't seem to work here, so I'm using the ``was_error`` flag instead.
                if (!was_error) {
                    was_error = false;
                    show_error("The connection to the CodeChat server was closed. Re-run the CodeChat extension to restart it.");
                }
                connection = undefined;
                // Since the connection is closed, we can't gracefully shut down the client via ``stop_client()``. Simply mark it as undefined so it will be re-created.
                client = undefined;
                id = undefined;
                idle_timer = undefined;
            });

            connection.on('connect', () => {
                get_render_client(context, connection);
            });
        } else {
            // If this was invoked while a connection is still pending, let that connection run its course.
            if (!connection.connection.connecting) {
                get_render_client(context, connection);
            }
        }
    }));
}


// On deactivation, close everything down.
export function deactivate() {
    // Return a promise that shuts down the server or stops the client, then do final cleanup.
    return new Promise(resolve => {
        if (client !== undefined) {
            // If we started the server, request a graceful shutdown.
            if (codechat_server?.is_server_running()) {
                client.shutdown_server(err => {
                    client = undefined;
                    id = undefined;
                    // Wait for the server to shut down.
                    setTimeout(() => {
                        resolve(err);
                    }, 500);
                });
            } else {
                // Otherwise, shut down the client.
                assert(id !== undefined);
                client.stop_client(id, err => {
                    client = undefined;
                    id = undefined;
                    resolve(err);
                });
            }
        } else {
            // With no client, there's nothing to do in this phase of the shutdown.
            resolve("");
        }
    }).then(() => {
        // Perform final cleanup.
        panel?.dispose();
        panel = undefined;
        connection?.end();
        connection = undefined;
        codechat_server?.terminal.dispose();
        codechat_server = undefined;
    });
}


// CodeChat services
// =================
// Get the render client from the CodeChat server and place it in the web view. Then, start a render.
function get_render_client(context: vscode.ExtensionContext, connection: thrift.Connection | undefined) {
    // There must already be a connection before this is called.
    assert(connection !== undefined);
    // Get a client if needed.
    if (client === undefined) {
        client = thrift.createClient(EditorPlugin, connection);
    }
    // Get a render client if needed.
    if (id === undefined) {
        client.get_client(
            client_location,
            function(err, render_client_return) {
                if (err !== null) {
                    show_error(`Communication error getting render client: ${err}`);
                    stop_client();
                } else if (render_client_return.error === "") {
                    // For a browser location, the panel shouldn't exist and the HTML should be empty. Otherwise, assign the HTML to the panel.
                    if (panel === undefined) {
                        assert(client_location === ttypes.CodeChatClientLocation.browser);
                        assert(render_client_return.html === "");
                    } else {
                        panel.webview.html = render_client_return.html;
                    }

                    // Save the ID just provided.
                    assert(id === undefined);
                    id = render_client_return.id;

                    // Render when the text is changed by listening for the correct `event <https://code.visualstudio.com/docs/extensionAPI/vscode-api#Event>`_.
                    context.subscriptions.push(vscode.workspace.onDidChangeTextDocument( (event) => {
                        start_render();
                    }));

                    // Render when the active editor changes.
                    context.subscriptions.push(vscode.window.onDidChangeActiveTextEditor( (event) => {
                        start_render();
                    }));

                    // Render when the webveiw panel is shown (if we have it -- we might be using an external browser).
                    if (panel !== undefined) {
                        context.subscriptions.push(panel.onDidChangeViewState( (event) => {
                            start_render();
                        }));
                    }

                    // Do an initial render.
                    start_render();
                } else {
                    show_error(`Error getting render client: ${render_client_return.error}`);
                    stop_client();
                }
            }
        );
    } else {
        // If the render client already exists, simply perform a render.
        start_render();
    }
}


// This is called after an event such as an edit, or when the CodeChat panel becomes visible. Wait a bit in case any other events occur, then request a render.
function start_render() {
    if (can_render()) {
        // Render after some inactivity: cancel any existing timer, then ...
        if (idle_timer !== undefined) {
            clearTimeout(idle_timer);
        }
        // ... schedule a render after 300 ms.
        idle_timer = setTimeout(() => {
            if (can_render()) {
                client!.start_render(
                    vscode.window.activeTextEditor!.document.getText(),
                    vscode.window.activeTextEditor!.document.fileName,
                    id!,
                    vscode.window.activeTextEditor!.document.isDirty,
                    (err, start_render_return) => {
                        if (err !== null) {
                            show_error(`Communication error when rendering: ${err}`)
                        } else if (start_render_return !== "") {
                            show_error(`Error when rendering: ${start_render_return}`);
                        }
                    }
                );
            }
        }, 300);
    }
}


// Gracefully shut down the render client if possible. Shut down the client as well.
function stop_client() {
    if ((client !== undefined) && (id !== undefined)) {
        client.stop_client(
            id,
            function(err, stop_client_return) {
                if (err !== null) {
                    show_error(`Communication error when stopping the client: ${err}`)
                } else if (stop_client_return !== "") {
                    show_error(`Error when stopping the client: ${stop_client_return}`);
                }
            }
        );
    }

    // Even though the callbacks to ``stop_client`` haven't completed yet, set this now to prevent further use of the client, which is stopping.
    client = undefined;
    id = undefined;

    // Shut the timer down after the client is undefined, to ensure it can't be started again by a call to ``start_render()``.
    if (idle_timer !== undefined) {
        clearTimeout(idle_timer);
        idle_timer = undefined;
    }
}


// Supporting functions
// ====================
// Provide an error message in the panel if possible.
function show_error(message: string) {
    if (panel !== undefined) {
        // If the panel was displaying other content, reset it for errors.
        if (!panel.webview.html.startsWith("<h1>CodeChat</h1>")) {
            panel.webview.html = "<h1>CodeChat</h1>";
        }
        panel.webview.html += `<p>${escape(message)}</p>`;
    } else {
        vscode.window.showErrorMessage(message);
    }
}


// Only render if the window and editor are active, we have a valid render client, and the webview is visible.
function can_render(): boolean {
    return (
        vscode.window.state.focused &&
        (vscode.window.activeTextEditor !== undefined) &&
        (id !== undefined) &&
        (client !== undefined) &&
        // If rendering in an external browser, the CodeChat panel doesn't need to be visible.
        ((client_location === ttypes.CodeChatClientLocation.browser) ||
        ((panel !== undefined) && panel.visible))
    );
}


// This runs the CodeChat Server in a psuedoterminal, imitating the way VSCode runs a build. Specifically, it opens a terminal, then runs the server there. Before the server starts, it displays a message in the terminal showing what command is being run. When the server exits, it also displays an exit message in the terminal.
function create_CodeChat_terminal() {
    // These emitters allow us to fire events (write and close) programmatically.
    const writeEmitter = new vscode.EventEmitter<string>();
    const closeEmitter = new vscode.EventEmitter<number>();
    let server_process: child_process.ChildProcess | undefined = undefined;

    const is_server_running = () => {
        return server_process?.exitCode === null;
    }

    const run_server = () => {
        // If the server is already running, return.
        if (is_server_running()) {
            return;
        }

        // Get the command from the VSCode configuration.
        const codechat_server_command = vscode.workspace.getConfiguration("CodeChat.CodeChatServer").get("Command");
        assert(typeof codechat_server_command === "string");

        // Split it into a command and args.
        let [command, ...args] = shlex.split(codechat_server_command);

        // Run it in a VSCode terminal.
        assert(typeof command === "string");
        writeEmitter.fire(`\x1B[1m> Executing the CodeChat Server: ${command} ${args.join(" ")} <\n\r\n\rPress any key to stop the server.\x1B[0m\n\r\n\r`)
        server_process = child_process.spawn(command, args);

        // Handle events.
        let post_str = "\n\r\n\rThis terminal will be reused by the CodeChat Server; to restart the server, re-run the CodeChat extension. To close this terminal, press any key.\x1B[0m\n\r\n\r";
        server_process.on("error", (err: NodeJS.ErrnoException) => {
            let msg = err.code === "ENOENT" ? `Error - cannot find the file ${err.path}` : err;
            writeEmitter.fire(`\n\r\n\r\x1B[1m> While running CodeChat server: ${msg} <${post_str}`)
        });
        server_process.on("exit", (code, signal) => {
            let exit_str = code ? `code ${code}` : `signal ${signal}`;
            writeEmitter.fire(`\n\r\n\r\x1B[1m> CodeChat Server exited with ${exit_str}. <${post_str}`);
            server_process = undefined;
        });
        assert(server_process.stdout !== null);
        server_process.stdout.on("data", (chunk) => writeEmitter.fire(chunk.toString()));
    };

    const pty: vscode.Pseudoterminal = {
        onDidWrite: writeEmitter.event,
        onDidClose: closeEmitter.event,
        // Important: don't run the server until this event is called; otherwise, the terminal isn't ready and will ignore any text sent to it. See the ``open`` method of `Pseudoterminal <https://code.visualstudio.com/api/references/vscode-api#Pseudoterminal>`_.
        open: run_server,
        close: () => {
            server_process?.kill();
            server_process = undefined;
            codechat_server = undefined;
        },
        handleInput: data => {
            if (is_server_running()) {
                // The server is running. Stop it.
                server_process!.kill();
                server_process = undefined;
            } else {
                // The server isn't running. Close the window.
                closeEmitter.fire(0);
            }
        }
    };

    const terminal = vscode.window.createTerminal({name: "CodeChat Server", pty});

    codechat_server = {
        run_server: run_server,
        is_server_running: is_server_running,
        terminal: terminal
    };
}