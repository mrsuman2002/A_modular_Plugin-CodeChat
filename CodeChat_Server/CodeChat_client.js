function run_client(id) {
    var transport = new Thrift.TXHRTransport("http://127.0.0.1:5000");
    var protocol  = new Thrift.TJSONProtocol(transport);
    var client    = new Web_SyncClient(protocol);
    var status_div = document.getElementById("status");
    var outputElement = document.getElementById("output");
    var build_div = document.getElementById("build");

    function do_get_result() {
        client.get_result(id, function(result) {
            if (result.gr_type == Get_Result_Type.html) {
                outputElement.srcdoc = result.text;
            } else if (result.gr_type == Get_Result_Type.build) {
                build_div.innerHTML = result.text;
            } else if (result.gr_type == Get_Result_Type.status) {
                status_div.innerHTML = result.text;
            } else {
                console.log("Unknown Get_Result_Type:", result.gr_type);
            }

            do_get_result();
        });
    }
    do_get_result();
}
