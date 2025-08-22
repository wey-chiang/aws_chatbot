import argparse
import os
import sys

from dotenv import load_dotenv

from aws_chatbot.chatbot import AWSChatbot


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="AWS Chatbot - Query AWS resources using natural language"
    )
    parser.add_argument(
        "--format",
        choices=["natural", "json", "table"],
        default="natural",
        help="Output format (default: natural)",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Show detailed execution steps"
    )
    parser.add_argument(
        "query", nargs="?", help="Query to execute (interactive mode if not provided)"
    )

    args = parser.parse_args()

    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print(
            "Error: OPENAI_API_KEY environment variable not set. Set it in the .env file or export it using: export OPENAI_API_KEY='your-key-here'"
        )
        sys.exit(1)

    try:
        chatbot = AWSChatbot(openai_key, verbose=args.verbose)
    except Exception as e:
        print(f"Error initializing chatbot: {e}")
        sys.exit(1)

    if args.query:
        result = chatbot.query(args.query, args.format)
        print(result)
    else:
        print("AWS Chatbot - Interactive Mode")
        print("Type 'exit' or 'quit' to leave")
        print("-" * 40)

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() in ["exit", "quit"]:
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
