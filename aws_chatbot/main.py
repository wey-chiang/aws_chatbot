import argparse
import os
import sys

from dotenv import load_dotenv

from aws_chatbot.chatbot import AWSChatbot
from aws_chatbot.prompts import INTERACTIVE_PROMPT

EXIT_COMMANDS = ["quit", "exit"]


def load_env_and_args():
    load_dotenv()

    parser = argparse.ArgumentParser(description="AWS Chatbot - Query AWS resources using natural language")
    parser.add_argument(
        "--format",
        choices=["natural", "json", "table"],
        default="natural",
        help="Output format (default: natural)",
    )
    parser.add_argument("--verbose", action="store_true", help="Show detailed execution steps")
    parser.add_argument("query", nargs="?", help="Query to execute (interactive mode if not provided)")

    args = parser.parse_args()

    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print(
            "Error: OPENAI_API_KEY environment variable not set. Set it in the .env file or export it using: export OPENAI_API_KEY='your-key-here'"
        )
        sys.exit(1)
    return args, openai_key


def main():
    args, openai_key = load_env_and_args()

    try:
        chatbot = AWSChatbot(openai_key, verbose=args.verbose)
    except Exception as e:
        print(f"Error initializing chatbot: {e}")
        sys.exit(1)

    if args.query:
        result = chatbot.query(args.query, args.format)
        print(result)
    else:
        print(INTERACTIVE_PROMPT.format(exit_commands=" or ".join(x for x in EXIT_COMMANDS), spacer="-" * 40))

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() in EXIT_COMMANDS:
                    print("Goodbye!")
                    break

                if query:
                    print("\nProcessing...\n")
                    result = chatbot.query(query, args.format)
                    print(result)

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")


if __name__ == "__main__":
    main()
