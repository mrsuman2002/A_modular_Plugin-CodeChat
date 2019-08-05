// *****************************************
// |docname| - This is a Thrift File
// *****************************************

namespace cpp tutorial
namespace d tutorial
namespace dart tutorial
namespace java tutorial
namespace php tutorial
namespace perl tutorial
namespace haxe tutorial
namespace netcore tutorial

enum Get_result_type { 
   html,
   build,
   status,
}

struct Get_result_return{
   Get_result_type gr_type,
   string text,
}

service CodechatSyc  {
   void ping(),
   string render(string text, string path),
   Get_result_return get_result(i32 id),
   string render_client(),
   void start_render(1:string text, string path, i32 id),
   void stop_render_client(i32 id)
}


