import json

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from tabulate import tabulate

from aws_chatbot.prompts import CHATBOT_SYSTEM_PROMPT
from aws_chatbot.tools import AWSCodeExecutorTool


class AWSChatbot:
    def __init__(self, openai_api_key: str, verbose: bool = False):
        self.llm = ChatOpenAI(api_key=openai_api_key, model="gpt-4", temperature=0)

        self.tools = [AWSCodeExecutorTool()]

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", CHATBOT_SYSTEM_PROMPT),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        agent = create_openai_tools_agent(self.llm, self.tools, prompt)

        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=verbose,
            handle_parsing_errors=True,
            max_iterations=3,
        )

    def query(self, question: str, output_format: str = "natural") -> str:
        try:
            response = self.agent_executor.invoke({"input": question})

            if output_format == "json":
                try:
                    lines = response["output"].split("\n")
                    for line in lines:
                        if line.strip().startswith("{") or line.strip().startswith("["):
                            return line.strip()
                    return response["output"]
                except:
                    return response["output"]
            elif output_format == "table":
                return self._format_as_table(response["output"])
            else:
                return response["output"]

        except Exception as e:
            return f"Error processing query: {str(e)}"

    @staticmethod
    def _format_as_table(output: str) -> str:
        try:
            lines = output.split("\n")
            for line in lines:
                if line.strip().startswith("{"):
                    data = json.loads(line.strip())
                    if isinstance(data, dict):
                        rows = []
                        for k, v in data.items():
                            if isinstance(v, (list, dict)):
                                v = json.dumps(v)
                            rows.append([k, v])
                        return tabulate(rows, headers=["Key", "Value"], tablefmt="grid")
            return output
        except:  # noqa
            return output
