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
// This extension creates a webview, then uses CodeChat services to render editor text in that webview.
//
//
// Requires
// ========
import vscode = require('vscode');
import thrift = require('thrift');
import assert = require('assert');
import EditorPlugin = require('./gen-nodejs/EditorPlugin');
import ttypes = require('./gen-nodejs/CodeChat_Services_types');
import escape = require('escape-html');


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

// A unique instance of these variables is required for each CodeChat panel. However, this code doesn't have a good UI way to deal with multiple panels, so only one is supported at this time.
let id: number | undefined = undefined;
let panel: vscode.WebviewPanel | undefined = undefined;
let idle_timer: NodeJS.Timeout | undefined = undefined;


// Activation
// ==========
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
            panel.webview.html = "`<html><h1>CodeChat</h1><p>Loading...</p></html>";
        } else {
            vscode.window.showInformationMessage("CodeChat is loading in an external browser...");
        }

        if (connection === undefined) {
            // The client should never exist if there's no connection.
            assert(client === undefined);

            // Try to connect to the CodeChat server. The `createConnection function <https://github.com/apache/thrift/blob/master/lib/nodejs/lib/thrift/connection.js#L258>`_ wraps `net.createConnection <https://nodejs.org/api/net.html#net_net_createconnection_options_connectlistener>`_ then returns a `Connection object <https://github.com/apache/thrift/blob/master/lib/nodejs/lib/thrift/connection.js#L35>`_.
            connection = thrift.createConnection("localhost", 9090, {
                transport: thrift.TBufferedTransport,
                protocol:  thrift.TBinaryProtocol,
                connect_timeout: 5,
                timeout: 5,
            });

            let was_error: boolean = false;

            connection.on('error', function(err) {
                was_error = true;
                show_error(`Error communicating with the CodeChat server: ${escape(err.message)}. Re-run the CodeChat extension to restart it.`);
                // The close event will be `emitted next <https://nodejs.org/api/net.html#net_event_error_1>`_; that will handle cleanup.
            });

            connection.on('close', (hadError) => {
                // If there was an error, the event handler above already provided the message. Note: the `parameter hadError <https://nodejs.org/api/net.html#net_event_close_1>`_ doesn't seem to work here, so I'm using the ``was_error`` flag instead.
                if (!was_error) {
                    was_error = false;
                    show_error("The connection to the CodeChat server was closed. Re-run the CodeChat extension to restart it.");
                }
                connection = undefined;
                // Since the connection is closed, we can't gracefully shut down the client via `stop_client()`. Simply mark it as undefined so it will be re-created.
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


// Provide an error message in the panel if possible.
function show_error(message: string) {
    if (panel !== undefined) {
        panel.webview.html = `<html><h1>CodeChat</h1><p>${escape(message)}</p></html>`;
    } else {
        vscode.window.showErrorMessage(message);
    }
}


// On deactivation, close everything down.
export function deactivate() {
    idle_timer = undefined;
    panel?.dispose();
    panel = undefined;
    stop_client();
    connection?.end();
    connection = undefined;
    client = undefined;
    id = undefined;
}


// CodeChat services
// =================
// Get the render client from the CodeChat server and place it in the web view.
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

    client = undefined;
    id = undefined;

    // Shut the timer down after the client is undefined, to ensure it can't be started again by a call to `start_render()`.
    if (idle_timer !== undefined) {
        clearTimeout(idle_timer);
    }
}
