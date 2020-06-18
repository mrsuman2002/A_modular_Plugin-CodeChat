// *********
// |docname|
// *********
// This implements the CodeChat client.
function run_client(id)
{
    // Create the client to communiate with the CodeChat server.
    let transport = new Thrift.TXHRTransport("/client");
    let protocol  = new Thrift.TJSONProtocol(transport);
    let client    = new CodeChatClientClient(protocol);

    // Get commonly-used nodes in the DOM.
    let status_message = document.getElementById("status_message");
    let build_progress = document.getElementById("build_progress");
    let status_errors_div = document.getElementById("status_errors");
    let outputElement = document.getElementById("output");
    let build_div = document.getElementById("build");
    let build_contents = document.getElementById("build_contents");
    let errors_div = document.getElementById("errors");

    // Set up "globals" for the function below.
    //
    // True if the output/errors should be cleared on the next result.
    let clear_output = false;
    // True if there were warnings or errors in the last build.
    let errors_or_warnings = false;
    // The size of the splitter, with a key of ``errors_or_warnings``.
    let splitter_size = {
        true: 85,
        false: 100,
    }

    // Wait for a server response, then update.
    function do_get_result() {

        client.get_result(id, function(result) {
            if (result.get_result_type === GetResultType.html) {
                // Save and restore scroll location through the content update.
                let scrollX = outputElement.contentWindow.scrollX;
                let scrollY = outputElement.contentWindow.scrollY;
                // See ideas in https://stackoverflow.com/a/16822995. Works for same-domain only.
                outputElement.onload = function () {
                    status_message.innerHTML = "Build complete.";
                    build_progress.style.display = "none";
                    outputElement.style.opacity = 1;
                    this.contentWindow.scrollBy(scrollX, scrollY);
                    // Get new content only *after* the load finishes. The case to avoid:
                    //
                    // #.   One load stores the x, y coordinates and begins to load a new page. This sets the scroll bars to 0.
                    // #.   Before the load finishes, another request comes. The x, y coordinates are saved as 0.
                    // #.   The first load finishes, but scrolls to 0, 0; the second load finish does the same.
                    do_get_result();
                };

                // Set the new src to (re)load content.
                outputElement.src = window.location.protocol + '//' + window.location.host + window.location.pathname + "/" + id + "/" + result.text;
                // The next build output received will apply to the new build, so set the flag.
                clear_output = true;
                // See comments above -- avoid double loads.
                return;

            } else if (result.get_result_type === GetResultType.build) {
                if (clear_output) {
                    // This is the start of a new build.
                    status_message.innerHTML = "Building...";
                    build_progress.style.display = "inline";
                    build_div.textContent = result.text;
                    errors_div.textContent = "";
                    status_errors_div.innerHTML = "";

                    // Save the current splitter state.
                    splitter_size[errors_or_warnings] = get_splitter().percent;

                    // Show that the current output HTML is old.
                    outputElement.style.opacity = 0.5;

                    clear_output = false;
                } else {
                    build_div.textContent += result.text;
                }
                // Scroll to the bottom, to show the content just added.
                scroll_to_bottom(build_contents);

            } else if (result.get_result_type === GetResultType.errors) {
                if (clear_output) {
                    // There was no build output, so just update the errors.
                    build_div.textContent = "";
                    errors_div.textContent = result.text;
                    // Save the current splitter state.
                    splitter_size[errors_or_warnings] = get_splitter().percent;
                    clear_output = false;
                } else {
                    errors_div.textContent += result.text;
                }
                // Scroll to the bottom, to show the content just added.
                scroll_to_bottom(build_contents);

                // Update the errors/warnings and splitter position.
                [errors_div.innerHTML, status_errors_div.innerHTML, errors_or_warnings] =
                    parse_for_errors(errors_div.innerHTML);
                set_splitter_percent(splitter_size[errors_or_warnings]);

            } else if (result.get_result_type === GetResultType.command) {
                if (result.text === "shutdown") {
                    // Close this window -- see https://stackoverflow.com/a/54787080.
                    window.open('', '_self').close();
                    // Stop asking for results.
                    return;
                } else if (result.text.startsWith("unknown client ")) {
                    console.log(result.text);
                    // Close the window -- there's no point in asking for more commands.
                    window.open('', '_self').close();
                } else {
                    console.log("Unknown command " + result.text);
                }

            } else {
                console.log("Unknown GetResultType:", result.get_result_type);
            }

            // Repeat to handle the next result.
            do_get_result();
        });
    }

    addEvent(window, 'load', function () {
        // Start listening to the server.
        do_get_result();
    });

    // The let statement below makes this accessible globally.
    navigate_to_error = function(file_path, line) {
        // TODO.
        console.log(file_path, line);
    };
}

let navigate_to_error;

// Utilities
// =========
// Get the splitter element.
function get_splitter() {
    return document.getElementById("splitter");
}


// Set the splitter percentage
function set_splitter_percent(percent) {
    let splitter = get_splitter();
    splitter.percent = percent;
    splitMe.update(splitter);
}


// Scroll an element to the bottom
function scroll_to_bottom(element) {
    element.scrollTop = element.scrollHeight - element.clientHeight;
}


// Parse the error output for errors and warnings.
function parse_for_errors(errors_html) {
    // This code parses the error string to determine get the number of
    // warnings and errors. Common docutils error messages read::
    //
    //  <string>:1589: (ERROR/3) Unknown interpreted text role "ref".
    //
    //  X:\ode.py:docstring of sympy:5: (ERROR/3) Unexpected indentation.
    //
    // and common sphinx errors read::
    //
    //  X:\SVM_train.m.rst:2: SEVERE: Title overline & underline mismatch.
    //
    //  X:\indexs.rst:None: WARNING: image file not readable: a.jpg
    //
    //  X:\conf.py.rst:: WARNING: document isn't included in any toctree
    //
    //  In Sphinx 1.6.1:
    //  X:\file.rst: WARNING: document isn't included in any toctree
    //
    // Each error/warning occupies one line. The following `regular
    // expression
    // <https://docs.python.org/2/library/re.html#regular-expression-syntax>`_
    // is designed to find the error position (1589/None) and message
    // type (ERROR/WARNING/SEVERE). Extra spaces are added to show which
    // parts of the example string it matches. For more details about
    // Python regular expressions, refer to the
    // `re docs <https://docs.python.org/2/library/re.html>`_.
    //
    // Examining this expression one element at a time::
    //
    //   <string>:1589:        (ERROR/3)Unknown interpreted text role "ref".
    let errPosRe =
        // The filename is anything up to the colon (but don't include newlines).
        "^([^:\\n]*)" +
        // Find the first occurence of a pair of colons, or just a single colon.
        // Between them there can be numbers or "None" or nothing. For example,
        // this expression matches the string ":1589:" or string ":None:" or
        // string "::" or the string ":". Next::
        ":(\\d*|None):? ";

    //   <string>:1589:        (ERROR/3)Unknown interpreted text role "ref".
    let errTypeRe = "\\(?(WARNING|ERROR|SEVERE)";
    // Next match the error type, which can
    // only be "WARNING", "ERROR" or "SEVERE". Before this error type the
    // message may optionally contain one left parenthesis.
    //
    let errEolRe = '.*$';
    // Since one error message occupies one line, a ``*``
    // quantifier is used along with end-of-line ``$`` to make sure only
    // the first match is used in each line.

    let regex = new RegExp(errPosRe + errTypeRe + errEolRe,
        // The message usually contain multiple lines; search each line
        // for errors and warnings.
        "m" +
        // The global flag must be present to replace all occurrances.
        "g");
    // Use findall to return all matches in the message, not just the first.
    let errNum = 0;
    let warningNum = 0;
    // The replacement function is called with the match text then each matched group.
    errors_html = errors_html.replace(regex, function (match_text, file_path, line, error_string) {
        if ((error_string === "ERROR") || (error_string === "SEVERE")) {
            ++errNum;
        } else if (error_string === "WARNING") {
            ++warningNum;
        }

        // Unsanitize the file name.
        let div = document.createElement("div");
        div.innerHTML = file_path;
        file_path = div.textContent;
        // Make an unspecificed filename empty.
        if (file_path === "<string>") {
            file_path = "";
        }

        // Clean up the line.
        if ((line === "None") || (line === "")) {
            line = -1;
        }

        // Create a hyperlink to nagivate to the error.
        return `<a href='javascript:navigate_to_error(${JSON.stringify(file_path)}, ${line})' class="error_link">${match_text}</a>`;
    });

    // Report these results to the user.
    let span_class;
    if (errNum) {
        span_class = "have_errors";
    } else if (warningNum) {
        span_class = "have_warnings";
    } else {
        span_class = "no_errors_or_warnings";
    }
    return [
        errors_html,
        `<span class="${span_class}">Error(s): ${errNum}, warning(s): ${warningNum}</span>`,
        errNum + warningNum > 0
    ];
}
