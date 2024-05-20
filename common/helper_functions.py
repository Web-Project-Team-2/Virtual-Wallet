from datetime import datetime

from fastapi import HTTPException, status


def convert_to_datetime(expiry_str: str) -> datetime:
    try:
        # Parse the expiry string in mm/yy format
        expiry_date = datetime.strptime(expiry_str, '%m/%y')
        return expiry_date
    except ValueError as e:
        # Handle the case where the input string is not in the expected format
        print(f"Error: {e}")
        return None


def check_password(password):
        if not any(char.isupper() for char in password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Password must contain at least one uppercase letter.')
        if not any(char.isdigit() for char in password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Password must contain at least one digit.')
        if not any(char in "!@#$%^&*()_+{}|:\"<>?[];',./\\" for char in password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Password must contain at least one special symbol.')

        return password
