var thrift = require('thrift');
var CodechatSyc = require('./gen-nodejs/CodechatSyc');
const vscode = require('vscode');
const assert = require('assert');

//creating a function name myfunc to import it in extension.js
function myfunc(webview){

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

  //function name ping
  client.ping(function(err, response){
    console.log('ping()');
  });

  //Function name render
  client.render(
    vscode.window.activeTextEditor.document.getText(),
      vscode.window.activeTextEditor.document.fileName, function(err, response) {
      console.log("client even works");
      console.log(response);
      webview.html=response;
      connection.end();
  });

//close the connection once we're done
}

//exporting myfunc to extension.js
exports.myfunc=myfunc
