// *****************************************
// |docname| - This is an Extension
// *****************************************
const vscode = require('vscode');
var tools = require('./JavaScript_Client/Client');
var subscription;
var panel;
function activate(context) {
    console.log('Congratulations, your extension "CodeChat" is now active!');
    let disposable = vscode.commands.registerCommand('extension.sayHello', function () {
        vscode.window.showInformationMessage('Hello Codechat');
        
// Creating and showing panel vscode.window.createWebviewPanel('CodeChat', "CodeChat", vscode.ViewColumn.One,{ here we should enable JS});
// -----------------------------------------------------------------------------------------------------------------------------------------
        panel = vscode.window.createWebviewPanel('CodeChat', "CodeChat", vscode.ViewColumn.One, 
        {
            //JavaScript is disabled in webviews by default, but it can easily re-enable by passing in the enableScripts: true option.
            // Enable scripts in the webview
            enableScripts: true
        });
// Calling function from Client.js named myfunc
// ---------------------------------------------
        tools.render_clientfunc(panel.webview);
        // tools.start_renderfunc(panel.webview);

// break client in two one render client and one render
// render_client will have client require
    });
    context.subscriptions.push(disposable);
// Taking the event from webview so that it can be used in OnDidChangeTextDocument
// ---------------------------------------------------------------------------------
    var listener = function(event) {
        console.log("It happened", event);
        tools.start_renderfunc(panel.webview);
    };

    // Starts listening for the `event <https://code.visualstudio.com/docs/extensionAPI/vscode-api#Event>`_.
    // ---------------------------------------------------------------------------------------------------------
    subscription = vscode.workspace.onDidChangeTextDocument(listener);
}

exports.activate = activate;
function deactivate() {
    subscription.dispose(); // stop listening
}
exports.deactivate = deactivate;







