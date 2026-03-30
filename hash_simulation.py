import os
import hashlib
import base64

# -----------------------------
# STEP 1: Generate random salt
# -----------------------------
def generate_salt(length=16):
    raw = os.urandom(length)  # random bytes from OS
    return base64.urlsafe_b64encode(raw).decode()[:22]  # mimic bcrypt style


# -----------------------------
# STEP 2: Fake "bcrypt-like" hash
# -----------------------------
def fake_bcrypt(password: str, salt: str, rounds: int = 12):
    data = (password + salt).encode()

    print("\n[Hashing Process Start]")
    print(f"Initial data: password + salt = {password + salt}")

    # simulate "cost"
    for i in range(2 ** rounds):
        data = hashlib.sha256(data).digest()

        # print only first few rounds so terminal doesn't explode
        if i < 3:
            print(f" Round {i+1}: {data.hex()[:32]}...")

    final_hash = base64.urlsafe_b64encode(data).decode()[:31]

    print(f"\nFinal hash (31 chars): {final_hash}")
    return final_hash


# -----------------------------
# STEP 3: Create stored password
# -----------------------------
def create_password_hash(password: str):
    salt = generate_salt()
    cost = 12

    print("\n--- SIGNUP ---")
    print(f"Generated salt: {salt}")
    print(f"Cost factor: {cost}")

    hash_part = fake_bcrypt(password, salt, cost)

    stored = f"$fake${cost}${salt}{hash_part}"
    print(f"\nStored value in DB:\n{stored}")

    return stored


# -----------------------------
# STEP 4: Verify password
# -----------------------------
def verify_password(input_password: str, stored: str):
    print("\n--- LOGIN ---")
    print(f"Stored value: {stored}")

    # extract parts
    parts = stored.split("$")
    cost = int(parts[2])
    combined = parts[3]

    salt = combined[:22]
    stored_hash = combined[22:]

    print(f"Extracted salt: {salt}")
    print(f"Extracted hash: {stored_hash}")
    print(f"Cost: {cost}")

    # recompute
    print("\nRecomputing hash with input password...")
    new_hash = fake_bcrypt(input_password, salt, cost)

    print("\n--- COMPARISON ---")
    print(f"New hash     : {new_hash}")
    print(f"Stored hash  : {stored_hash}")

    if new_hash == stored_hash:
        print("\n✅ MATCH → LOGIN SUCCESS")
    else:
        print("\n❌ NO MATCH → LOGIN FAILED")


# -----------------------------
# MAIN EXECUTION
# -----------------------------
if __name__ == "__main__":
    password = input("Enter password for signup: ")
    stored = create_password_hash(password)

    print("\n\nNow try logging in...\n")

    attempt = input("Enter password for login: ")
    verify_password(attempt, stored)
