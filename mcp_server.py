from mcp.server.fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware
from starlette.applications import Starlette

from logging_config import get_logger
from config import config
from tools.report_tools import register_report_analysis_tools

logger = get_logger(__name__)


class FastMCPWithCORS(FastMCP):
    def sse_app(self, mount_path: str | None = None) -> Starlette:
        app = super().sse_app(mount_path)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=str(config.server.cors_origins).split(","),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        return app

    def run(self, transport: str = "sse"):
        import uvicorn

        host = config.server.host
        port = config.server.port

        if transport == "sse":
            app = self.sse_app()
            uvicorn.run(app, host=host, port=port)
        else:
            super().run(transport)


mcp = FastMCPWithCORS("saudi-location-intelligence", port=config.server.port)

register_report_analysis_tools(mcp)


def main():
    logger.info("Starting MCP server on http://%s:%s/sse", config.server.host, config.server.port)
    mcp.run("sse")


if __name__ == "__main__":
    main()