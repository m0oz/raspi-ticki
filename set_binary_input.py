from src.projector import Projector


def main():
    projector = Projector()

    while True:
        try:
            user_input = input("Enter 40-bit binary data or 'exit' to quit: ").replace(" ", "")
            if user_input.lower() == "exit":
                break

            if len(user_input) != 40 or not all(c in "01" for c in user_input):
                print("Invalid input. Please enter exactly 40 bits of binary data.")
                continue

            projector.send_binary_event(user_input)
        except Exception as e:
            print(f"An error occurred: {e}")


main()
