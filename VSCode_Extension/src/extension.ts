// *****************************************************
// |docname| - The CodeChat Visual Studio Code extension
// *****************************************************
// This extension creates a webview, then uses CodeChat services to render editor text in that webview.
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
let connection: thrift.Connection;
let client: EditorPlugin.Client;
let id: number;


// Activation
// ==========
// This is invoked when the extension is activated. TODO: wrong entry point -- need something called just once per session, not every time the command is invoked. Invoking the command should just make the tab containing the client visible.
export function activate(context: vscode.ExtensionContext) {
    let disposable = vscode.commands.registerCommand('extension.codeChat', function () {

        // Try to connect to the CodeChat server.
        connection = thrift.createConnection("localhost", 9090, {
            transport: thrift.TBufferedTransport,
            protocol:  thrift.TBinaryProtocol,
            connect_timeout: 5,
            timeout: 5,
        });

        connection.on('error', function(err) {
            vscode.window.showInformationMessage('CodeChat error connecting to server: ' + err.message);
        });

        // Use this to create an editor plugin client for the CodeChat server.
        client = thrift.createClient(EditorPlugin, connection);

        // Create a web view which will display CodeChat output.
        var panel = vscode.window.createWebviewPanel(
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

        // Get the render client from the CodeChat server and place it in the web view.
        client.get_client(
            // For debug, make this ``ttypes.CodeChatClientLocation.browser``, which allows easier inspection of what's going on.
            ttypes.CodeChatClientLocation.browser,
            function(err, render_client_return) {
                if (err !== null) {
                    vscode.window.showInformationMessage('CodeChat communication error when creating a client: ' + err)
                } else if (render_client_return.error === "") {
                    panel.webview.html = render_client_return.html;
                    id = render_client_return.id;

                    // Do an initial render.
                    start_render();
                } else {
                    vscode.window.showInformationMessage('CodeChat error when creating a client: ' + render_client_return.error);
                }
        });
    });
    context.subscriptions.push(disposable);

    // Render when the text is changed by listening for the correct `event <https://code.visualstudio.com/docs/extensionAPI/vscode-api#Event>`_.
    disposable = vscode.workspace.onDidChangeTextDocument(function(event) {
        start_render();
    });
    context.subscriptions.push(disposable);
}


export function deactivate() {
    client.stop_client(
        id,
        function(err, stop_client_return) {
            if (err !== null) {
                vscode.window.showInformationMessage('CodeChat communication error when creating a client: ' + err)
            } else if (stop_client_return !== "") {
                vscode.window.showInformationMessage("CodeChat error when stopping the client: " + stop_client_return);
            }
        });
    connection.end();
}


// CodeChat services
// =================
function start_render() {
    // Only render if an editor is active.
    if (vscode.window.activeTextEditor !== undefined) {
        client.start_render(
            vscode.window.activeTextEditor.document.getText(),
            vscode.window.activeTextEditor.document.fileName,
            id,
            function(err, start_render_return) {
                if (err !== null) {
                    vscode.window.showInformationMessage('CodeChat communication error when creating a client: ' + err)
                } else if (start_render_return !== "") {
                    vscode.window.showInformationMessage("CodeChat error when rendering: " + start_render_return);
                }
            }
        );
    }
}
