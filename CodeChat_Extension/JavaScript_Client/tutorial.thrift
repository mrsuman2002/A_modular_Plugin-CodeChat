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


service CodechatSyc  {
   void ping(),
   string render(1:string text,2:string path)
   void render_client()
   void start_render(1:string text, 2:string path, 3:int id)
   int stop_render_client(2:int id)
}


