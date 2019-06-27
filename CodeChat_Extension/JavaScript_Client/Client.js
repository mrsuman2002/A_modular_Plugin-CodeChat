// *****************************************
// |docname| - This is a JavaScript Client
// *****************************************

var thrift = require('thrift');
var CodechatSyc = require('./gen-nodejs/CodechatSyc');
const vscode = require('vscode');
const assert = require('assert');




// Creating a function name myfunc to import it in `../../CodeChat_Extension/extension.js`
// -----------------------------------------------------------------------------------------

function render_clientfunc(webview){
  var transport = thrift.TBufferedTransport;
  var protocol = thrift.TBinaryProtocol;
  var connection = thrift.createConnection("localhost", 9090, {
    transport : transport,
    protocol : protocol
  });
  connection.on('error', function(err) {
    assert(false, err);
  });
  var client = thrift.createClient(CodechatSyc, connection);  

  client.render_client(
      function(err, response) {
      console.log("render client even works");
      console.log(response);
      webview.html=response;
      connection.end();
      });
}

function start_renderfunc(){
  var transport = thrift.TBufferedTransport;
  var protocol = thrift.TBinaryProtocol;
  var connection = thrift.createConnection("localhost", 9090, {
    transport : transport,
    protocol : protocol
  });
  connection.on('error', function(err) {
    assert(false, err);
  });
  var client = thrift.createClient(CodechatSyc, connection); 

client.start_render(
  vscode.window.activeTextEditor.document.getText(),
    vscode.window.activeTextEditor.document.fileName, 
    1,
    function(err, response) {
    console.log("start render  even works");
    console.log(response);
    connection.end();
    });
}


// Exporting myfunc to extension.js
// ----------------------------------
exports.render_clientfunc=render_clientfunc;
exports.start_renderfunc=start_renderfunc;
