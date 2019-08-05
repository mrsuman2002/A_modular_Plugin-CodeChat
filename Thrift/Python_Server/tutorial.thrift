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

enum get_result_type { 
   html,
   build,
   status,
}

struct get_result_return{
   1: get_result_type gr_type,
   2: string text,
}

service CodechatSyc  {
   void ping(),
   string render(1:string text, 2:string path),
   get_result_return get_result(1:i32 id),
   string render_client(),
   void start_render(1:string text, 2:string path, 3:i32 id),
   void stop_render_client(1:i32 id)
}


