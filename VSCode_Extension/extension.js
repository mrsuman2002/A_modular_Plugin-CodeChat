// *****************************************************
// |docname| - The CodeChat Visual Studio Code extension
// *****************************************************
// This extension create a webview, then uses CodeChat services to render editor text in the webview.
//
//
// Requires
// ========
const vscode = require('vscode');
const thrift = require('thrift');
const assert = require('assert');
const Editor_Extension = require('./gen-nodejs/Editor_Extension');

// Globals
// =======
var subscription;
var connection;
var client;


// Activation
// ==========
// This is invoked when the extension is activated (once per session?)
function activate(context) {
    let disposable = vscode.commands.registerCommand('extension.sayHello', function () {
        vscode.window.showInformationMessage('CodeChat activated.');

        // Connect to the CodeChat server.
        connection = thrift.createConnection("localhost", 9090, {
            transport: thrift.TBufferedTransport,
            protocol:  thrift.TBinaryProtocol,
        });
        
        connection.on('error', function(err) {
            assert(false, err);
        });
        
        client = thrift.createClient(Editor_Extension, connection);
        
        // Create a web view which will display CodeChat output. 
        var panel = vscode.window.createWebviewPanel('CodeChat', "CodeChat", 
            vscode.ViewColumn.One, { enableScripts: true });

        // Get the render client from the CodeChat server and place it in the web view.
        client.render_client(
            function(err, html) {
                panel.webview.html = html;

                // Do an initial render.
                start_renderfunc();
        });
    });
    context.subscriptions.push(disposable);

    // Render when the text is changed by listening for the correct `event <https://code.visualstudio.com/docs/extensionAPI/vscode-api#Event>`_.
    subscription = vscode.workspace.onDidChangeTextDocument(function(event) {
        start_renderfunc();
    });
}


function deactivate() {
    subscription.dispose();
    connection.end();
}


// CodeChat services
// =================
function start_renderfunc() {
    client.start_render(
        vscode.window.activeTextEditor.document.getText(),
        vscode.window.activeTextEditor.document.fileName, 
        // TODO: a dynamically-chosen ID.
        1,
        function(err) {
    });
}


// Exports
// =======
exports.activate = activate;
exports.deactivate = deactivate;