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
// ***************************************************************************
// |docname| - Core code for the CodeChat client
// ***************************************************************************
// Constants
// =========
// .. _GetResultType JS:
//
// These must match the `constants in the server <GetResultType Py>`.
const GetResultType = {
    html: 0,
    build: 1,
    errors: 2,
    command: 3,
}


// Core client
// ===========
// Given an ID to use, run the CodeChat client.
function run_client(id, ws_address)
{
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
    let clear_output = true;
    // True if the most recent reload was caused by the user; false if this was a programmatic reload.
    let is_user_navigation = false;
    // True if there were warnings or errors in the last build.
    let errors_or_warnings = false;
    // The size of the splitter, with a key of ``errors_or_warnings``.
    let splitter_size = {
        true: 85,
        false: 100,
    }

    // Create a websocket to communicate with the CodeChat server.
    let ws = new ReconnectingWebSocket(ws_address);

    // Identify this client on connection.
    ws.onopen = event => ws.send(JSON.stringify(id))

    // Handle messages.
    ws.onmessage = event => {
        result = JSON.parse(event.data);
        if (result.get_result_type === GetResultType.html) {
            // Save and restore scroll location through the content update, if we can.
            let [scrollX, scrollY] = getScroll();
            // See ideas in https://stackoverflow.com/a/16822995. Works for same-domain only.
            outputElement.onload = function () {
                // Only run this once, not every time the user navigates in the browser. Otherwise, each click would call ``do_get_result`` again, producing multiple get_result requests at the same time.
                outputElement.onload = undefined;
                if (is_user_navigation) {
                    console.log("TODO: User navigation.");
                } else {
                    status_message.innerHTML = "Build complete.";
                    build_progress.style.display = "none";
                    outputElement.classList.remove("building");
                    // Restore the scroll location if we were able to save it.
                    if ( (scrollX !== undefined) && (scrollY !== undefined) ) {
                        this.contentWindow.scrollBy(scrollX, scrollY);
                    }
                    // The programmatic reload is done -- anything else that happens now is from the user.
                    is_user_navigation = true;
                    // Get new content only *after* the load finishes. The case to avoid:
                    //
                    // #.   One load stores the x, y coordinates and begins to load a new page. This sets the scroll bars to 0.
                    // #.   Before the load finishes, another request comes. The x, y coordinates are saved as 0.
                    // #.   The first load finishes, but scrolls to 0, 0; the second load finish does the same.
                }
            };

            // Set the new src to (re)load content.
            outputElement.src = window.location.protocol + '//' + window.location.host + window.location.pathname + "/" + id + "/" + result.text;
            // The next build output received will apply to the new build, so set the flag.
            clear_output = true;
            // See comments above -- avoid double loads and indicate that the is a programmatic reload.
            is_user_navigation = false;
            // Exit for now; the callbacks above will continue this function's operation.
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

                // _`class building`: Show that the current output HTML is old.
                outputElement.classList.add("building");

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
                // Close this window -- see https://stackoverflow.com/a/54787080. See `close the window`_.
                outputElement.srcdoc = "<html><body><p>The CodeChat client was shut down. Please close this window.</p></body></html>";
                build_div.textContent = "";
                errors_div.textContent = "";
                status_message.innerHTML = "Client shut down.";
                window.open('', '_self').close();
                // Stop asking for results.
                return;
            } else if (result.text.startsWith("error: unknown client ")) {
                console.log(result.text);
                // _`Close the window` -- there's no point in asking for more commands. Note: there are some cases where this fails, although I've only seen this once. From the Chrome console, ``Scripts may close only the windows that were opened by them.`` In this case, leave a message asking the user to close the window.
                outputElement.srcdoc = "<html><body><p>CodeChat client error: lost connection to the CodeChat server. Close this window and restart the editor plug-in.</p></body></html>";
                build_div.textContent = "";
                errors_div.textContent = "";
                status_message.innerHTML = "Server disconnected";
                window.open('', '_self').close();
                // Stop asking for results.
                return;
            } else {
                console.log("Unknown command " + result.text);
            }

        } else {
            console.log("Unknown GetResultType:", result.get_result_type);
        }
    };

    // Return the X and Y coordinates of the scrollbar of the output iframe if possible.
    function getScroll() {
        try {
            // This is only allowed for same-domain origins -- for example, if the user clicks on a link in the docs that goes to an external website, then the following lines will raise an exception.
            return [outputElement.contentWindow.scrollX, outputElement.contentWindow.scrollY];
        } catch (err) {
            return [undefined, undefined];
        }
    }

    // Start requesting results as soon as the web page is loaded.
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


// This regex parses the error string to determine get the number of warnings and errors.
const error_regex = new RegExp(
    // Common docutils error messages read::
    //
    //  <string>:1589: (ERROR/3) Unknown interpreted text role "ref".
    //
    //  X:\ode.py:docstring of sympy:5: (ERROR/3) Unexpected indentation.
    //
    // and common Sphinx errors read::
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
    // The CodeChat renderer also produces `error messages <_checkModificationTime>`_ formatted in a similar way so they'll be identified by the same regex::
    //
    //  X:\ode.py:: ERROR: CodeChat renderer - source file older than the html file X:\_build\html\ode.py.
    //
    // Each error/warning occupies one line. The following `regular
    // expression <https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_Expressions>`_ is designed to find the error position (1589/None) and message type (ERROR/WARNING/SEVERE). Extra spaces are added to show which parts of the example string it matches.
    //
    // Examining the following expression one element at a time::
    //
    //   <string>:1589:        (ERROR/3)Unknown interpreted text role "ref".
    //
    // The filename is anything up to the colon. Windows filenames may begin with a drive letter followed by a colon -- don't capture this (the leading ``?:``).
    "^((?:\\w:)?[^:]*)" +
    // Find the first occurrence of a pair of colons, or just a single colon. Between them there can be numbers or "None" or nothing. For example, this expression matches the string ":1589:" or string ":None:" or the string "::" or the string ":".
    ":(\\d*|None):? " +

    // Next match the error type, which can only be "WARNING", "ERROR" or "SEVERE". Before this error type the message may optionally contain one left parenthesis.
    "\\(?(WARNING|ERROR|SEVERE)" +

    // Since one error message occupies one line, a ``*`` quantifier is used along with end-of-line ``$`` to make sure only the first match is used in each line.
    ".*$",

    // The message usually contains multiple lines; search each line for errors and warnings.
    "m" +
    // The global flag must be present to replace all occurrences.
    "g"
);


// Parse the error output for errors and warnings.
function parse_for_errors(errors_html) {
    let errNum = 0;
    let warningNum = 0;
    // The replacement function is called with the match text then each matched group.
    errors_html = errors_html.replace(error_regex, function (match_text, file_path, line, error_string) {
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
