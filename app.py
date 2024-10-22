import random
import string
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

import json
import os

# Initialize Firebase
if not firebase_admin._apps:
    cred_data = json.loads(os.environ['FIREBASE_CREDENTIALS'])
    cred = credentials.Certificate(cred_data)
    firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

def generate_random_password(length):
    lower_case_letters = string.ascii_lowercase
    upper_case_letters = string.ascii_uppercase
    digits = string.digits
    special_characters = string.punctuation

    password = [
        random.choice(upper_case_letters),
        random.choice(digits),
        random.choice(special_characters)
    ]

    all_characters = lower_case_letters + upper_case_letters + digits + special_characters
    password += [random.choice(all_characters) for _ in range(length - len(password))]
    random.shuffle(password)

    return ''.join(password)

def generate_random_password_with_selection(length, include_uppercase, include_lowercase, include_digits, include_special):
    lower_case_letters = string.ascii_lowercase if include_lowercase else ''
    upper_case_letters = string.ascii_uppercase if include_uppercase else ''
    digits = string.digits if include_digits else ''
    special_characters = string.punctuation if include_special else ''

    if not (lower_case_letters or upper_case_letters or digits or special_characters):
        raise ValueError("At least one character type must be selected")

    all_characters = lower_case_letters + upper_case_letters + digits + special_characters
    password = []

    if include_uppercase:
        password.append(random.choice(upper_case_letters))
    if include_lowercase:
        password.append(random.choice(lower_case_letters))
    if include_digits:
        password.append(random.choice(digits))
    if include_special:
        password.append(random.choice(special_characters))

    password += [random.choice(all_characters) for _ in range(length - len(password))]
    random.shuffle(password)

    return ''.join(password)

def generate_custom_password(length, required_chars):
    password = []
    for chars in required_chars.values():
        password.extend(chars)

    if len(password) > length:
        raise ValueError("The number of specified characters exceeds the desired length")

    all_characters = string.ascii_letters + string.digits + string.punctuation
    remaining_length = length - len(password)
    if remaining_length > 0:
        password.extend(random.choices(all_characters, k=remaining_length))

    random.shuffle(password)

    return ''.join(password)

def save_to_firebase(username, password):
    print(f"Attempting to save user: {username}, password: {password}")
    try:
        # Add user data to the 'users' collection
        doc_ref_tuple = db.collection('users').add({
            'username': username,
            'password': password
        })
        # Extract document ID from the returned tuple
        doc_ref = doc_ref_tuple[1] if isinstance(doc_ref_tuple, tuple) else doc_ref_tuple
        print(f"User saved with ID: {doc_ref.id if hasattr(doc_ref, 'id') else 'unknown'}")
        return doc_ref.id if hasattr(doc_ref, 'id') else None
    except Exception as e:
        print(f"Failed to save user: {e}")  # Print the error to debug
        return None


def main():
    st.title("Password Generator")

    username = st.text_input("Enter your username:")
    length = st.number_input("Enter the desired password length (at least 4 characters):", min_value=4)

    method = st.radio("Choose a password generation method:", ("Simple random generation", "Select character types", "Specify required characters"))

    if method == "Simple random generation":
        if st.button("Generate Password"):
            password = generate_random_password(length)
            st.success(f"Generated password: **{password}**")
            if username:
                user_id = save_to_firebase(username, password)
                if user_id:
                    st.success(f"User saved with ID: {user_id}")
                else:
                    st.error("Failed to save user to Firebase. Check the console for details.")
            else:
                st.error("Please enter a username.")

    elif method == "Select character types":
        include_uppercase = st.checkbox("Include uppercase letters")
        include_lowercase = st.checkbox("Include lowercase letters")
        include_digits = st.checkbox("Include digits")
        include_special = st.checkbox("Include special characters")

        if st.button("Generate Password"):
            try:
                password = generate_random_password_with_selection(length, include_uppercase, include_lowercase, include_digits, include_special)
                st.success(f"Generated password: **{password}**")
                if username:
                    user_id = save_to_firebase(username, password)
                    if user_id:
                        st.success(f"User saved with ID: {user_id}")
                    else:
                        st.error("Failed to save user to Firebase. Check the console for details.")
                else:
                    st.error("Please enter a username.")
            except ValueError as e:
                st.error(str(e))

    elif method == "Specify required characters":
        required_upper = st.text_input("Enter required uppercase letters (e.g., ABC):")
        required_lower = st.text_input("Enter required lowercase letters (e.g., abc):")
        required_digits = st.text_input("Enter required digits (e.g., 123):")
        required_special = st.text_input("Enter required special characters (e.g., !@#):")

        required_chars = {
            'uppercase': required_upper,
            'lowercase': required_lower,
            'digit': required_digits,
            'special': required_special
        }

        if st.button("Generate Password"):
            try:
                password = generate_custom_password(length, required_chars)
                st.success(f"Generated password: **{password}**")
                if username:
                    user_id = save_to_firebase(username, password)
                    if user_id:
                        st.success(f"User saved with ID: {user_id}")
                    else:
                        st.error("Failed to save user to Firebase. Check the console for details.")
                else:
                    st.error("Please enter a username.")
            except ValueError as e:
                st.error(str(e))

if __name__ == "__main__":
    main()
    

