from typing import Type

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from aws_chatbot.executor import SafeCodeExecutor


class CodeExecutorInput(BaseModel):
    code: str = Field(description="Python code using boto3 to execute")


class AWSCodeExecutorTool(BaseTool):
    name: str = "execute_aws_code"
    description: str = """Execute Python code that uses boto3 to query AWS resources.
    The code should use boto3 to interact with AWS services and print results as JSON.
    Available imports: boto3, json
    Always handle exceptions and print structured output."""
    args_schema: Type[BaseModel] = CodeExecutorInput
    executor: Type[SafeCodeExecutor] = SafeCodeExecutor

    def __init__(self):
        super().__init__()
        self.executor = SafeCodeExecutor(timeout_seconds=30)  # noqa

    def _run(self, code: str) -> str:
        return self.executor.execute(code)
