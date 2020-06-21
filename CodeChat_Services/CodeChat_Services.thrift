// ************************************
// |docname| - Define CodeChat services
// ************************************
// This file defines a set of CodeChat services provided by the CodeChat server.
//
// Implementation draft
// ====================
// Draft of a `Thrift <https://thrift.apache.org/>`_ interface between the text editor extension and the CodeChat server, and between the web browser client and the CodeChat server:
//
// -    Extension service:
//
//      -   ``void sync_to(string text, uint text_index, uint global_y_coordinate_of_cursor)``
//      -   ``uint index, string text, enum result_type { sync, text, request_ownership } = get_results()`` returns:
//
//          -   The index for the next sync request made in the web view. Valid if result_type == sync.
//          -   Updated text for the editor. Valid if result_type == text.
//
// -    ``void grant_ownswership(int id)``
//
// -    Web browser service. All methods raise an exception if the id isn't valid.
//
//      -   ``void sync_to(string text, uint text_index, uint global_y_coordinate_of_cursor)``
//      -   ``void request_ownership(int id)`` returns when ownership is granted.
//
// Edits may be made in the text editor or in the web view. To prevent users from modifying both at the same time, only one of these two places may have editing priviledges. The text editor begins with this priviledge; the web view must request and obtain it from the text editor before allowing edits. Privledges return to the text editor when the web view sends updated text. What if the text editor changes to another document while the web view is still editing? Probably pop up a modal dialog in the web page: save changes or discard changes.


// CodeChat server
// ===============
struct RenderClientReturn {
    // An HTML string which contains either the render client or an URL for the client.
    1: string html,
    // The ID for this client.
    2: i32 id,
    // An empty string on success, or an error message.
    3: string error
}


// Define the location of the CodeChat client.
enum CodeChatClientLocation {
    // A URL, which the CodeChat plugin will host in its own web browser.
    url,
    // An HTML string, which the CodeChat plugin will host in its own web browser.
    html,
    // An external browser, which the CodeChat server should launch.
    browser
}

// Provide CodeChat services to editor plugins.
service EditorPlugin  {
    // Create a CodeChat client and return HTML for it and its ID.
    RenderClientReturn get_client(
        // The location of the client to return.
        1: CodeChatClientLocation codeChat_client_location
    ),

    // Render the provided text as html. Returns an empty string on success, or an error message.
    string start_render(
        // The source code or text to render.
        1: string text,
        // The path to this source file; may be blank for an unnamed file.
        2: string path,
        // _`id`: The ID of the client to render in.
        3: i32 id,
        // True if the document is dirty (modified), fale if clean.
        4: bool is_dirty
    ),

    // Release all resources associated with a CodeChat client. Returns an empty string on success, or an error message.
    string stop_client(
        // See id_.
        1:i32 id
    )
 }


// CodeChat client
// ===============
// The type of result returned by get_result_.
enum GetResultType {
    // A URL indicating that new content is available.
    html,
    // A build output message.
    build,
    // Errors from the build
    errors,
    // A command
    command,
}

// The return type for get_result_.
struct GetResultReturn {
    1: GetResultType get_result_type,
    2: string text,
}


// Provide CodeChat services to the web browser.
 service CodeChatClient {
     // _`get_result`: Ask the server for an update.
    GetResultReturn get_result(1: i32 id),
 }