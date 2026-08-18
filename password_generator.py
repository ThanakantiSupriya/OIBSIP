"""
Random Password Generator - Beginner Tier
Task 3 (Oasis Infobyte)

Features:
- Prompt for password length (minimum 8 enforced)
- Choose character types: uppercase, lowercase, numbers, symbols (>=2 required)
- Generate and display a password matching the criteria
- Input validation (invalid lengths / no types selected)
- Loop to generate another password without restarting
"""

import random
import string

MIN_LENGTH = 8


def get_length():
    while True:
        raw = input(f"Enter desired password length (minimum {MIN_LENGTH}): ")
        cleaned = raw.strip().strip('"').strip("'")
        digits_only = "".join(ch for ch in cleaned if ch.isdigit())

        if not digits_only:
            print("Please enter a valid whole number (e.g. 12).\n")
            continue

        length = int(digits_only)
        if length < MIN_LENGTH:
            print(f"Length must be at least {MIN_LENGTH}. Try again.\n")
            continue

        return length


def get_character_types():
    print("\nChoose character types to include (select at least 2):")
    print("  1. Uppercase letters (A-Z)")
    print("  2. Lowercase letters (a-z)")
    print("  3. Numbers (0-9)")
    print("  4. Symbols (!@#$%^&* etc.)")

    while True:
        raw = input("Your choice (e.g. 1,2,3 or 1 2 3): ").strip()

        if not raw:
            print("You didn't enter anything. Please type at least two numbers from 1-4.\n")
            continue

        cleaned = raw.replace(",", " ")
        parts = cleaned.split()
        valid = {"1", "2", "3", "4"}
        invalid_parts = [p for p in parts if p not in valid]

        if invalid_parts:
            print(f"'{raw}' isn't valid input. Only enter numbers 1-4.\n")
            continue

        choices = set(parts)
        if len(choices) < 2:
            print("You must select at least 2 character types (e.g. 1,3).\n")
            continue

        pools = []
        if "1" in choices:
            pools.append(string.ascii_uppercase)
        if "2" in choices:
            pools.append(string.ascii_lowercase)
        if "3" in choices:
            pools.append(string.digits)
        if "4" in choices:
            pools.append("!@#$%^&*()-_=+[]{};:,.<>?/")

        return pools


def generate_password(length, pools):
    password_chars = [random.choice(pool) for pool in pools]
    all_chars = "".join(pools)
    remaining = length - len(password_chars)
    password_chars += [random.choice(all_chars) for _ in range(remaining)]
    random.shuffle(password_chars)
    return "".join(password_chars)


def main():
    print("=== Random Password Generator (Beginner Tier) ===\n")
    while True:
        length = get_length()
        pools = get_character_types()
        password = generate_password(length, pools)
        print(f"\nGenerated Password: {password}\n")

        again = input("Generate another password? (y/n): ").strip().lower()
        if again != "y":
            print("Goodbye!")
            break
        print()


if __name__ == "__main__":
    main()