from functools import wraps
from flask import session, redirect, url_for
import string
import random
from deep_translator import GoogleTranslator
import re


"""״״״
This function checks if the password is valid
"""
def check_password(password : str):
    msg = []
    if len(password) < 8 or len(password) > 14:
        msg.append("Password must be between 8 and 14 characters")
    if not any(char.isdigit() for char in password):
        msg.append("Password must contain at least one digit")
    if not any(char.isupper() for char in password):
        msg.append("Password must contain at least one uppercase letter")
    if not any(char.islower() for char in password):
        msg.append("Password must contain at least one lowercase letter")
    if not any(char.isalnum() for char in password):
        msg.append("Password must contain at least one alphanumeric character")
    return msg

"""This function is a decorator that checks if the user is logged in"""
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

"""This function generates a random join code"""
def generate_join_code(length=6):
    letters_and_digits = string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

"""This function converts an english name to a hebrew name using the GoogleTranslator API"""
def convert_to_hebrew_ai(english_name):
    clean_name = re.sub(r'[^a-zA-Z]', '', english_name)
    try:
        translator = GoogleTranslator(source='en', target='iw')
        hebrew_name = translator.translate(clean_name)
        return hebrew_name
    except Exception as e:
        print(f"Translation failed: {e}")
        return clean_name