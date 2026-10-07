import sys
from src.agent import run_agent
from src.logger import logging
from src.exception import MyCustomException

def main():
    print("==================================================")
    print("      Personal Finance AI Agent (Groq Powered)    ")
    print("==================================================")
    print("Type 'exit' or 'quit' to end the session.\n")
    print("Ask question using user id (USR101)")

    while True:
        try:
            user_input = input("User > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break

            response = run_agent(user_input)
            print(f"\nAgent > {response}\n")

        except KeyboardInterrupt:
            print("\nExiting session...")
            break
        except Exception as e:
            logging.error(f"Error in CLI execution loop: {str(e)}")
            print(f"\nAn error occurred: {str(e)}\n")
        except Exception as e:
            raise MyCustomException(e,sys)

if __name__ == "__main__":
    main()