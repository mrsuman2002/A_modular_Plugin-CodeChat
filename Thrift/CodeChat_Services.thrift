// ************************************
// |docname| - Define CodeChat services
// ************************************
// This file defines a set of CodeChat services provided by the CodeChat server.

enum Get_Result_Type { 
    html,
    build,
    status,
}

struct Get_Result_Return {
    1:Get_Result_Type gr_type,
    2:string text,
}

// Provide CodeChat services to editor extensions.
service Editor_Extension  {
    // TODO: return the ID, along with a string.
    string render_client(),
    void start_render(1:string text, 2:string path, 3:i32 id),
    void stop_render_client(1:i32 id)
 }


// Provide CodeChat services to the web browser.
 service Web_Sync {
    Get_Result_Return get_result(1:i32 id),
 }