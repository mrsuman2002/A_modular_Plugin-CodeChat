***********************
Security considerations
***********************
The CodeChat System performs most of its work using the CodeChat Server. This page discusses the security implications of running this server.

The server listens to three ports, as shown in `/docs/developer`:

-   The `CodeChat service port <CodeChat service port>` runs an `Apache Thrift <https://thrift.apache.org/>`_ server, which allows CodeChat extensions to render a file and perform other CodeChat-related functions.
-   The HTTP (webserver) port (see `CodeChat_Server/constants.py`) runs a `Bottle webserver <https://bottlepy.org/docs/dev/>`_, sending rendered files to the CodeChat Client.
-   The websocket port (also in `CodeChat_Server/constants.py`) provide a two-way control and status communication channel between the CodeChat Server and a CodeChat Client.

These ports should **never** be exposed publicly; they provide an attacker significant access to the underlying computer's filesystem. To mitigate this risk, the CodeChat Server by default only accepts connections from the computer it runs on, by binding only the ``LOCALHOST`` address defined in `CodeChat_Server/constants.py`.

**However**, the server also supports an optional insecure mode, in which it bypasses this protection by allowing connections from *any* computer. For example, `/extensions/VSCode/contents` can run on a remote Docker container using the `VS Code Remote Development <https://code.visualstudio.com/docs/remote/remote-overview>`_ toolset. In this mode, **attackers allowed to connect to these ports will have access to the server's filesystem**.

To improve security, **never expose these ports publicly**.