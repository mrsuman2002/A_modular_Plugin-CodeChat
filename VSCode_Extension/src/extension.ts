// *****************************************************
// |docname| - The CodeChat Visual Studio Code extension
// *****************************************************
// This extension creates a webview, then uses CodeChat services to render editor text in that webview.
//
// TODO:
//
// #.   Add sync requests in (required a second client).
//
// .. image:: x.png
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
let connection: thrift.Connection | undefined = undefined;
let client: EditorPlugin.Client;
// A unique instance of these variables is required for each CodeChat panel. However, this code doesn't have a good UI way to deal with multiple panels, so only one is supported at this time.
let id: number | undefined = undefined;
let panel: vscode.WebviewPanel | undefined = undefined;


// Activation
// ==========
// This is invoked when the extension is activated.
//
// Ideally, we could create one CodeChat panel per window, which would render whatever the focused editor in that window contained. However, there doesn't seem to be any way to determine the current window.
export function activate(context: vscode.ExtensionContext) {
    context.subscriptions.push(vscode.commands.registerCommand('extension.codeChat', () => {

        // Create or reveal the webview panel.
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
                    client.stop_client(
                        id,
                        function(err, stop_client_return) {
                            if (err !== null) {
                                vscode.window.showInformationMessage(`CodeChat communication error when stopping the client: ${err}`)
                            } else if (stop_client_return !== "") {
                                vscode.window.showInformationMessage(`CodeChat error when stopping the client: ${stop_client_return}`);
                            }
                        }
                    );
                    id = undefined;
                }
                panel = undefined;
            }));
        }

        // Provide a simple status display while the CodeChat plugin is starting up.
        //
        // Accumulate text in this variable.
        let startup_text = "";
        // Append and display it using this function.
        function show_startup(msg: string) {
            startup_text += msg;
            if (panel !== undefined) {
                panel.webview.html = `<html><h1>CodeChat</h1><p>${startup_text}<p></html>`;
            } else {
                assert(false);
            }
        };

        // Get the render client from the CodeChat server and place it in the web view.
        function get_render_client() {
            if (panel === undefined) {
                assert(false);
            } else {
                client.get_client(
                    // For debug, make this ``ttypes.CodeChatClientLocation.browser``, which allows easier inspection of what's going on.
                    ttypes.CodeChatClientLocation.html,
                    function(err, render_client_return) {
                        if (err !== null) {
                            show_startup(`<b>error</b>: ${err}`)
                        } else if (render_client_return.error === "") {
                            if (panel === undefined) {
                                assert(false);
                            } else {
                                panel.webview.html = render_client_return.html;
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

                                // Render when the webveiw panel is shown.
                                context.subscriptions.push(panel.onDidChangeViewState( (event) => {
                                    start_render();
                                }));

                                // Do an initial render.
                                start_render();
                            }
                        } else {
                            show_startup(`<b>error</b>: ${render_client_return.error}`);
                        }
                    }
                );
            }
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
                show_startup(`<b>error:</b> ${err.message}`);
                // Shut down the connection and mark as undefined so it will be re-created next run.
                connection?.destroy();
                connection = undefined;
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
    connection?.end();
}


// CodeChat services
// =================
function start_render() {
    // Only render if an editor is active, we have a valid render client, and the webview is visible.
    if (
        (vscode.window.activeTextEditor !== undefined) &&
        (id !== undefined) &&
        (panel?.visible)
    ) {
        client.start_render(
            vscode.window.activeTextEditor.document.getText(),
            vscode.window.activeTextEditor.document.fileName,
            id,
            function(err, start_render_return) {
                if (err !== null) {
                    vscode.window.showInformationMessage(`CodeChat communication error when creating a client: ${err}`)
                } else if (start_render_return !== "") {
                    vscode.window.showInformationMessage(`CodeChat error when rendering: ${start_render_return}`);
                }
            }
        );
    }
}
