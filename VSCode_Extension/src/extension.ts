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
// TODO:
//
// #.   Add sync requests in (required a second client).
//
//
// Requires
// ========
import vscode = require('vscode');
import thrift = require('thrift');
import assert = require('assert');
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
// A unique instance of these variables is required for each CodeChat panel. However, this code doesn't have a good UI way to deal with multiple panels, so only one is supported at this time.
let id: number | undefined = undefined;
let panel: vscode.WebviewPanel | undefined = undefined;
let idle_timer: NodeJS.Timeout | undefined = undefined;


// Activation
// ==========
// This is invoked when the extension is activated.
//
// Ideally, we could create one CodeChat panel per window, which would render whatever the focused editor in that window contained. However, there doesn't seem to be any way to determine the current window.
export function activate(context: vscode.ExtensionContext) {
    context.subscriptions.push(vscode.commands.registerCommand('extension.codeChat', () => {

        // Create or reveal the webview panel.
        if (client_location === ttypes.CodeChatClientLocation.html) {
            if (panel !== undefined) {
                // Since the panel already exists, make it visible.
                panel.reveal();
            } else {
                // Create a webview panel.
                panel = vscode.window.createWebviewPanel(
                    "CodeChat", "CodeChat",
                    {
                        // Without this, the focus becomes this webview, which allows the code window open before this command was execute to retain the focus and be immediately rendered.
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
                    if (id !== undefined) {
                        client?.stop_client(
                            id,
                            function(err, stop_client_return) {
                                if (err !== null) {
                                    vscode.window.showErrorMessage(`Communication error when stopping the client: ${err}`)
                                } else if (stop_client_return !== "") {
                                    vscode.window.showErrorMessage(`Error when stopping the client: ${stop_client_return}`);
                                }
                            }
                        );
                        id = undefined;
                    }
                    panel = undefined;
                }));
            }
        }

        // Provide a simple status display while the CodeChat system is starting up.
        //
        // Accumulate text in this variable.
        let startup_text = "";
        // Append and display it using this function.
        function show_startup(msg: string) {
            startup_text += msg;
            if (panel !== undefined) {
                panel.webview.html = `<html><h1>CodeChat</h1><p>${startup_text}<p></html>`;
            } else {
                vscode.window.showInformationMessage(msg);
            }
        };

        // Get the render client from the CodeChat server and place it in the web view.
        function get_render_client() {
            assert(client !== undefined);
            client?.get_client(
                client_location,
                function(err, render_client_return) {
                    if (err !== null) {
                        vscode.window.showErrorMessage(`Communication error getting render client: ${err}`)
                    } else if (render_client_return.error === "") {
                        if (panel === undefined) {
                            assert(client_location === ttypes.CodeChatClientLocation.browser);
                            assert(render_client_return.html === "");
                        } else {
                            panel.webview.html = render_client_return.html;
                        }

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
                        vscode.window.showErrorMessage(`Error getting render client: ${render_client_return.error}`);
                    }
                }
            );
        }

        if (connection === undefined) {
            // The client should never exist if there's no connection.
            assert(client === undefined);

            // Try to connect to the CodeChat server. The `createConnection function <https://github.com/apache/thrift/blob/master/lib/nodejs/lib/thrift/connection.js#L258>`_ wraps `net.createConnection <https://nodejs.org/api/net.html#net_net_createconnection_options_connectlistener>`_ then returns a `Connection object <https://github.com/apache/thrift/blob/master/lib/nodejs/lib/thrift/connection.js#L35>`_.
            show_startup("Connecting to the CodeChat engine...");
            connection = thrift.createConnection("localhost", 9090, {
                transport: thrift.TBufferedTransport,
                protocol:  thrift.TBinaryProtocol,
                connect_timeout: 5,
                timeout: 5,
            });

            connection.on('error', function(err) {
                vscode.window.showErrorMessage(`Error connecting: ${err.message}`);
                // Shut down the connection and client, marking them as undefined so they will be re-created next run.
                connection?.destroy();
                connection = undefined;
                client = undefined;
            });

            connection.on('connect', () => {
                show_startup("ok<br/>Requesting client...");

                // Use this to create an editor plugin client for the CodeChat server.
                if (connection !== undefined) {
                    client = thrift.createClient(EditorPlugin, connection);
                } else {
                    assert(false);
                }

                get_render_client();
            });
        } else {
            // If this was invoked while a connection is still pending, let that connection run its course.
            if (!connection.connection.connecting) {
                // If a connection exists, the client should have been created.
                assert(client !== undefined);

                // Get a render client if we don't have one.
                if (id === undefined) {
                    get_render_client();
                }
            }
        }
    }));
}


export function deactivate() {
    panel?.dispose();
    panel = undefined;

    connection?.end();
    connection = undefined;
}


// CodeChat services
// =================
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
                            vscode.window.showErrorMessage(`CodeChat communication error when rendering: ${err}`)
                        } else if (start_render_return !== "") {
                            vscode.window.showErrorMessage(`CodeChat error when rendering: ${start_render_return}`);
                        }
                    }
                );
            }
        }, 300);
    }
}

// Only render if an editor is active, we have a valid render client, and the webview is visible.
function can_render(): boolean {
    return (
        (vscode.window.activeTextEditor !== undefined) &&
        (id !== undefined) &&
        (client !== undefined) &&
        // If rendering in an external browser, the CodeChat panel doesn't need to be visible.
        ((client_location === ttypes.CodeChatClientLocation.browser) ||
        ((panel !== undefined) && panel.visible))
    );
}