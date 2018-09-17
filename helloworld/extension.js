// Entension 
const vscode = require('vscode');
var tools = require('./client_folder/Client');
function activate(context) {
    console.log('Congratulations, your extension "helloworld" is now active!');
    let disposable = vscode.commands.registerCommand('extension.sayHello', function () {

        vscode.window.showInformationMessage('Hello Suman!');
// Create and show panel
        const panel = vscode.window.createWebviewPanel('CodeChat', "CodeChat", vscode.ViewColumn.One, { });
// Calling function from Client.js named myfunc
        tools.myfunc(panel.webview);
    });
    context.subscriptions.push(disposable);
}

exports.activate = activate;
function deactivate() {
}
exports.deactivate = deactivate;


