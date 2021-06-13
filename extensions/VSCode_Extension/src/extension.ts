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
//
// Requirements
// ============
// Node.js packages
// ----------------
import assert = require("assert");
import child_process = require("child_process");

// Third-party packages
// --------------------
import escape = require("escape-html");
import shlex = require("shlex");
import thrift = require("thrift");
import vscode = require("vscode");

// Local packages
// --------------
import EditorPlugin = require("./gen-nodejs/EditorPlugin");
import ttypes = require("./gen-nodejs/CodeChat_Services_types");

// Globals
// =======
// These globals are truly global: only one is needed for this entire plugin.
//
// The Thrift network connection to the CodeChat Server.
let thrift_connection: thrift.Connection | undefined = undefined;
// The Thrift client using this connection.
let thrift_client: EditorPlugin.Client | undefined = undefined;
// Where the webclient resides: ``html`` for a webview panel embedded in VSCode; ``browser`` to use an external browser.
const codechat_client_location: ttypes.CodeChatClientLocation =
    ttypes.CodeChatClientLocation.html;
// The subprocess in which the CodeChat Server runs.
let codechat_terminal: CodeChatTerminal | undefined = undefined;
// True if the subscriptions to IDE change notifications have been registered.
let subscribed = false;

// A unique instance of these variables is required for each CodeChat panel. However, this code doesn't have a good UI way to deal with multiple panels, so only one is supported at this time.
//
// The id of this render client, assigned by the CodeChat Server.
let codechat_client_id: number | undefined = undefined;
// The webview panel used to display the CodeChat Client
let webview_panel: vscode.WebviewPanel | undefined = undefined;
// A timer used to wait for additional events (keystrokes, etc.) before performing a render.
let idle_timer: NodeJS.Timeout | undefined = undefined;

// Activation/deactivation
// =======================
// This is invoked when the extension is activated. It either creates a new CodeChat instance or reveals the currently running one.
export function activate(context: vscode.ExtensionContext) {
    context.subscriptions.push(
        vscode.commands.registerCommand("extension.codeChat", async () => {
            console.log("CodeChat extension starting.");

            if (!subscribed) {
                subscribed = true;

                // Render when the text is changed by listening for the correct `event <https://code.visualstudio.com/docs/extensionAPI/vscode-api#Event>`_.
                context.subscriptions.push(
                    vscode.workspace.onDidChangeTextDocument((event) => {
                        start_render();
                    })
                );

                // Render when the active editor changes.
                context.subscriptions.push(
                    vscode.window.onDidChangeActiveTextEditor((event) => {
                        start_render();
                    })
                );
            }

            // Create or reveal the webview panel; if this is an external browser, we'll open it after the client is created.
            if (codechat_client_location === ttypes.CodeChatClientLocation.html) {
                if (webview_panel !== undefined) {
                    // As below, don't take the focus when revealing.
                    webview_panel.reveal(undefined, true);
                } else {
                    // Create a webview panel.
                    webview_panel = vscode.window.createWebviewPanel(
                        "CodeChat",
                        "CodeChat",
                        {
                            // Without this, the focus becomes this webview; setting this allows the code window open before this command was executed to retain the focus and be immediately rendered.
                            preserveFocus: true,
                            // Put this in the a column beside the current column.
                            viewColumn: vscode.ViewColumn.Beside,
                        },
                        {
                            enableScripts: true,
                        }
                    );
                    // TODO: do I need to dispose of this and the following event handlers? I'm assuming that it will be done automatically when the object is disposed.
                    webview_panel.onDidDispose((event) => {
                        // Shut down the render client when the webview panel closes.
                        console.log("CodeChat extension: shut down webview.");
                        stop_client();
                        webview_panel = undefined;
                    });

                    // Render when the webveiw panel is shown.
                    webview_panel.onDidChangeViewState((event) => {
                        start_render();
                    });
                }
            }

            // Provide a simple status display while the CodeChat system is starting up.
            if (webview_panel !== undefined) {
                // If we have an ID, then the GUI is already running; don't replace it.
                if (codechat_client_id === undefined) {
                    webview_panel.webview.html = "<h1>CodeChat</h1><p>Loading...</p>";
                }
            } else {
                vscode.window.showInformationMessage(
                    "CodeChat is loading in an external browser..."
                );
            }

            if (codechat_terminal === undefined) {
                codechat_terminal = new CodeChatTerminal();
            }
            // Run the CodeChat Server; this is a no-op if the server is already running.
            try {
                await codechat_terminal.run_server();
            } catch (err) {
                console.log(`CodeChat extension: running server failed with ${err}.`);
            }

            // Show the terminal, in case there are errors. This helps the user understand what's going wrong in case of a failure.
            assert((codechat_terminal !== undefined) && (codechat_terminal.terminal !== undefined));
            codechat_terminal.terminal.show(true);

            if (thrift_connection === undefined) {
                console.log("CodeChat extension: creating Thrift client.");
                // The client should never exist if there's no connection.
                assert(thrift_client === undefined);

                // Try to connect to the CodeChat Server. The `createConnection function <https://github.com/apache/thrift/blob/master/lib/nodejs/lib/thrift/connection.js#L258>`_ wraps `net.createConnection <https://nodejs.org/api/net.html#net_net_createconnection_options_connectlistener>`_ then returns a `Connection object <https://github.com/apache/thrift/blob/master/lib/nodejs/lib/thrift/connection.js#L35>`_.
                //
                // This must use the `CodeChat service port <CodeChat service port>`.
                thrift_connection = thrift.createConnection("localhost", 9090, {
                    transport: thrift.TBufferedTransport,
                    protocol: thrift.TBinaryProtocol,
                });

                let was_error: boolean = false;

                thrift_connection.on("error", function (err) {
                    was_error = true;
                    show_error(
                        `Error communicating with the CodeChat Server: ${err.message}. Re-run the CodeChat extension to restart it.`
                    );
                    // The close event will be `emitted next <https://nodejs.org/api/net.html#net_event_error_1>`_; that will handle cleanup.
                });

                thrift_connection.on("close", (hadError) => {
                    console.log("CodeChat extension: closing Thrift connection.");
                    // BUG: on deactivation, VS Code closes this socket before calling the ``deactivate()`` method. This prevents us from shutting down the client. I'm not sure what event handler would allow me to perform cleanup before the socket is closed.

                    // If there was an error, the event handler above already provided the message. Note: the `parameter hadError <https://nodejs.org/api/net.html#net_event_close_1>`_ only applies to transmission errors, not to any other errors which trigger the error callback. Therefore, I'm using the ``was_error`` flag instead to catch non-transmission errors.
                    if (!was_error) {
                        if (hadError) {
                            show_error(
                                "The connection to the CodeChat Server was closed due to a transmission error. Re-run the CodeChat extension to restart it."
                            );
                        } else {
                            show_error(
                                "The connection to the CodeChat Server was closed. Re-run the CodeChat extension to restart it."
                            );
                        }
                    }
                    thrift_connection = undefined;
                    // Since the connection is closed, we can't gracefully shut down the client via ``stop_client()``. Simply mark it as undefined so it will be re-created.
                    thrift_client = undefined;
                    codechat_client_id = undefined;
                    idle_timer = undefined;
                });

                thrift_connection.on("connect", () => {
                    assert(thrift_connection !== undefined);
                    get_render_client(thrift_connection);
                });
            } else {
                // If this was invoked while a connection is still pending, let that connection run its course.
                if (!thrift_connection.connection.connecting) {
                    get_render_client(thrift_connection);
                } else {
                    console.log("CodeChat extension: connection already pending, so a new client wasn't created.");
                }
            }
        })
    );
}

// On deactivation, close everything down.
export async function deactivate() {
    console.log("CodeChat extension: deactivating.");
    console.log(thrift_client);
    // Return a promise that shuts down the server or stops the client, then do final cleanup.
    await new Promise((resolve) => {
        if (thrift_client !== undefined) {
            // If we started the server, request a graceful shutdown.
            console.log(codechat_terminal?.is_server_running());
            if (codechat_terminal?.is_server_running()) {
                thrift_client.shutdown_server((err) => {
                    thrift_client = undefined;
                    codechat_client_id = undefined;
                    // Wait for the server to shut down.
                    setTimeout(() => {
                        console.log("CodeChat extension: timeout for server shutdown complete.");
                        resolve(err);
                    }, 500);
                });
            } else {
                // Otherwise, shut down the client.
                assert(codechat_client_id !== undefined);
                thrift_client.stop_client(codechat_client_id, (err_1) => {
                    thrift_client = undefined;
                    codechat_client_id = undefined;
                    resolve(err_1);
                });
            }
        } else {
            // With no client, there's nothing to do in this phase of the shutdown.
            resolve("");
        }
    });
    // Perform final cleanup. The next line stops the ``idle_timer`` (the client is already stopped).
    stop_client();
    webview_panel?.dispose();
    thrift_connection?.end();
    thrift_connection = undefined;
    codechat_terminal?.terminal?.dispose();
    codechat_terminal = undefined;
    console.log("CodeChat extension: deactivated.");
}

// CodeChat services
// =================
// Get the render client from the CodeChat Server and place it in the web view. Then, start a render.
function get_render_client(
    connection: thrift.Connection
) {
    // Get a client if needed.
    if (thrift_client === undefined) {
        thrift_client = thrift.createClient(EditorPlugin, connection);
    }
    // Get a render client if needed.
    if (codechat_client_id === undefined) {
        console.log("CodeChat extension: requesting a render client.");
        thrift_client.get_client(
            codechat_client_location,
            function (err, render_client_return) {
                if (err !== null) {
                    show_error(
                        `Communication error getting render client: ${err}`
                    );
                    stop_client();
                } else if (render_client_return.error === "") {
                    // For a browser location, the panel shouldn't exist and the HTML should be empty. Otherwise, assign the HTML to the panel.
                    if (webview_panel === undefined) {
                        assert(
                            codechat_client_location ===
                                ttypes.CodeChatClientLocation.browser
                        );
                        assert(render_client_return.html === "");
                    } else {
                        webview_panel.webview.html = render_client_return.html;
                    }

                    // Save the ID just provided.
                    assert(codechat_client_id === undefined);
                    codechat_client_id = render_client_return.id;

                    // Do an initial render.
                    start_render();
                } else {
                    show_error(
                        `Error getting render client: ${render_client_return.error}`
                    );
                    stop_client();
                }
            }
        );
    } else {
        // If the render client already exists, simply perform a render.
        console.log("CodeChat extension: client already exists.");
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
                console.log(`CodeChat extension: starting render.`);
                thrift_client!.start_render(
                    vscode.window.activeTextEditor!.document.getText(),
                    vscode.window.activeTextEditor!.document.fileName,
                    codechat_client_id!,
                    vscode.window.activeTextEditor!.document.isDirty,
                    (err, start_render_return) => {
                        if (err !== null) {
                            show_error(
                                `Communication error when rendering: ${err}`
                            );
                        } else if (start_render_return !== "") {
                            show_error(
                                `Error when rendering: ${start_render_return}`
                            );
                        }
                    }
                );
            }
        }, 300);
    }
}

// Gracefully shut down the render client if possible. Shut down the client as well.
function stop_client() {
    console.log("CodeChat extension: stopping client.");
    if (thrift_client !== undefined && codechat_client_id !== undefined) {
        thrift_client.stop_client(codechat_client_id, function (err, stop_client_return) {
            if (err !== null) {
                show_error(
                    `Communication error when stopping the client: ${err}`
                );
            } else if (stop_client_return !== "") {
                show_error(
                    `Error when stopping the client: ${stop_client_return}`
                );
            }
        });
    }

    // Even though the callbacks to ``stop_client`` haven't completed yet, set this now to prevent further use of the client, which is stopping.
    thrift_client = undefined;
    codechat_client_id = undefined;

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
    if (webview_panel !== undefined) {
        // If the panel was displaying other content, reset it for errors.
        if (!webview_panel.webview.html.startsWith("<h1>CodeChat</h1>")) {
            webview_panel.webview.html = "<h1>CodeChat</h1>";
        }
        webview_panel.webview.html += `<p>${escape(message)}</p>`;
    } else {
        vscode.window.showErrorMessage(message);
    }
}

// Only render if the window and editor are active, we have a valid render client, and the webview is visible.
function can_render(): boolean {
    return (
        vscode.window.activeTextEditor !== undefined &&
        codechat_client_id !== undefined &&
        thrift_client !== undefined &&
        // If rendering in an external browser, the CodeChat panel doesn't need to be visible.
        (codechat_client_location === ttypes.CodeChatClientLocation.browser ||
            (webview_panel !== undefined && webview_panel.visible))
    );
}

// This runs the CodeChat Server in a pseudo-terminal, imitating the way VSCode runs a build. Specifically, it opens a terminal, then runs the server there. Before the server starts, it displays a message in the terminal showing what command is being run. When the server exits, it also displays an exit message in the terminal.
class CodeChatTerminal {
    // These emitters allow us to fire events (write and close) programmatically.
    writeEmitter = new vscode.EventEmitter<string>();
    closeEmitter = new vscode.EventEmitter<number>();
    server_process: child_process.ChildProcess | undefined = undefined;
    terminal: vscode.Terminal | undefined = undefined;

    is_server_running() {
        return this.server_process?.exitCode === null;
    }

    async run_server() {
        // If the server is already running, return.
        if (this.is_server_running()) {
            return;
        }

        // This promise is resolved if the server reports readiness or exits; it is rejected if running the server produces an error or if the timeout occurs.
        return new Promise((resolve, reject) => {
            // **Step 1:** define the core code to run the server.
            const _run_server = () => {
                // Get the command from the VSCode configuration.
                const codechat_server_command = vscode.workspace
                    .getConfiguration("CodeChat.CodeChatServer")
                    .get("Command");
                assert(typeof codechat_server_command === "string");

                // Split it into a command and args.
                let [command, ...args] = shlex.split(codechat_server_command);

                // Run it in a VSCode terminal.
                assert(typeof command === "string");
                this.writeEmitter.fire(
                    `\x1B[1m> Executing the CodeChat Server: ${command} ${args.join(
                        " "
                    )} <\n\r\n\rPress any key to stop the server.\x1B[0m\n\r\n\r`
                );
                this.server_process = child_process.spawn(command, args);
                // Reject the promise with a timeout if the server doesn't report success before then.
                setTimeout(reject, 5000, "timeout");

                // Handle events.
                let post_str =
                    "\n\r\n\rThis terminal will be reused by the CodeChat Server; to restart the server, re-run the CodeChat extension.\x1B[0m\n\r\n\r";
                this.server_process.on("error", (err: NodeJS.ErrnoException) => {
                    let msg =
                        err.code === "ENOENT"
                            ? `Error - cannot find the file ${err.path}`
                            : err;
                    this.writeEmitter.fire(
                        `\n\r\n\r\x1B[1m> While running the CodeChat Server: ${msg} <${post_str}`
                    );
                    // Indicate the server didn't start.
                    reject(err);
                });

                this.server_process.on("exit", (code, signal) => {
                    let exit_str = code ? `code ${code}` : `signal ${signal}`;
                    this.writeEmitter.fire(
                        `\n\r\n\r\x1B[1m> CodeChat Server exited with ${exit_str}. <${post_str}`
                    );
                    this.server_process = undefined;
                    // Indicate the server exiting; hopefully, this means another instance of the server is already running.
                    resolve(["exit", code, signal]);
                });

                let found_ready = false;
                const ready_regex = /\r?\nCODECHAT_READY\r?\n/;
                assert(this.server_process.stdout !== null);
                this.server_process.stdout.on("data", (chunk) => {
                    // Scan stdout for the code indicating the server is up.
                    const s = chunk.toString();
                    this.writeEmitter.fire(s);
                    if (!found_ready && ready_regex.test(s)) {
                        found_ready = true;
                        resolve("ready");
                    }
                });

                assert(this.server_process.stderr !== null);
                this.server_process.stderr.on("data", (chunk) =>
                    this.writeEmitter.fire(chunk.toString())
                );
            };

            // **Step 2:** Run the server (creating a terminal first if necessary).
            if (this.terminal !== undefined) {
                _run_server();
            } else {
                // If the terminal doesn't exist, create it. When the terminal is created, it will run the server from its startup code (the open callback).
                const pty: vscode.Pseudoterminal = {
                    onDidWrite: this.writeEmitter.event,
                    onDidClose: this.closeEmitter.event,
                    // Important: don't run the server until this event is called; otherwise, the terminal isn't ready and will ignore any text sent to it. See the ``open`` method of `Pseudoterminal <https://code.visualstudio.com/api/references/vscode-api#Pseudoterminal>`_.
                    open: _run_server,
                    close: () => {
                        this.server_process?.kill();
                        this.server_process = undefined;
                        codechat_terminal = undefined;
                    },
                    handleInput: () => {
                        if (this.is_server_running()) {
                            // The server is running. Stop it.
                            this.server_process!.kill();
                            this.server_process = undefined;
                        }
                    },
                };

                this.terminal = vscode.window.createTerminal({
                    name: "CodeChat Server",
                    pty: pty,
                });
            }
        });
    }
}
