from mcp.server.fastmcp import FastMCP
from pydantic import Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from config import config
from logging_config import get_logger
from utils import get_secret

logger = get_logger(__name__)


def _build_llm(model: str, temperature: float) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=model,
        temperature=temperature,
        google_api_key=get_secret("gemini_api_key"),
    )


def register_report_analysis_tools(mcp: FastMCP):
    @mcp.tool(
        name="report_analysis",
        description="""Analyze report content and answer questions using an LLM.

        Analysis Capabilities:
        - Read and understand report content passed as plain text
        - Answer specific questions about the report
        - Provide insights and explanations
        - Extract key findings and metrics

        Supported Report Types:
        - Any report whose text content has been extracted and passed by the caller

        Usage:
        - Takes plain text report content and a user question
        - Returns LLM-generated analysis and answers
        """,
    )
    async def report_analysis(
        report_contents: str = Field(description="Report content to analyze (raw HTML or plain text)"),
        user_query: str = Field(description="Question or analysis request about the report"),
        model: str = Field(default=config.llm.model, description="LLM model to use for analysis"),
        temperature: float = Field(default=config.llm.temperature, description="Temperature for LLM responses (0.0-1.0)"),
    ) -> str:
        try:
            logger.info("Analyzing report, query: %s", user_query[:80])

            llm = _build_llm(model, temperature)
            system_prompt = (
                config.report_analysis_agent.system_prompt
                + f"\n\nReport Content:\n{report_contents}\n"
            )

            response = llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_query),
            ])
            return response.content

        except Exception as e:
            logger.exception("Error in report_analysis")
            return f"Error analyzing report: {e}"