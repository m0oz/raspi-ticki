from src.projector import Projector


def main():
    projector = Projector()

    while True:
        try:
            user_input = input("Enter time (HH MM) or 'exit' to quit: ")
            if user_input.lower() == "exit":
                break

            hour, minute = map(int, user_input.split())

            if not (0 <= hour < 24) or not (0 <= minute < 60):
                print("Hour must be between 0 and 23, and minute must be between 0 and 59")
                continue

            projector.send_time(hour, minute)
        except ValueError:
            print("Invalid input. Please enter time as two integers (HH MM).")
        except Exception as e:
            print(f"An error occurred: {e}")


main()
