import io
import json
import signal
import sys
from contextlib import contextmanager

import boto3


class TimeoutException(Exception):
    pass


@contextmanager
def timeout(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException("Code execution timed out")

    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


class SafeCodeExecutor:
    def __init__(self, timeout_seconds: int = 30):
        self.timeout_seconds = timeout_seconds

    def execute(self, code: str) -> str:
        safe_builtins = {
            "print": print,
            "len": len,
            "range": range,
            "enumerate": enumerate,
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "list": list,
            "dict": dict,
            "set": set,
            "tuple": tuple,
            "sorted": sorted,
            "min": min,
            "max": max,
            "sum": sum,
            "any": any,
            "all": all,
            "isinstance": isinstance,
            "Exception": Exception,
            "__import__": __import__,
        }

        safe_globals = {
            "__builtins__": safe_builtins,
            "boto3": boto3,
            "json": json,
        }

        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()

        try:
            with timeout(self.timeout_seconds):
                exec(code, safe_globals, {})

            output = captured_output.getvalue()
            return (
                output
                if output
                else "Code executed successfully but produced no output"
            )

        except TimeoutException as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error executing code: {str(e)}"
        finally:
            sys.stdout = old_stdout
