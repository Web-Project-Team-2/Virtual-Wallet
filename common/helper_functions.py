from datetime import datetime


def convert_to_datetime(expiry_str: str) -> datetime:
    try:
        # Parse the expiry string in mm/yy format
        expiry_date = datetime.strptime(expiry_str, '%m/%y')
        return expiry_date
    except ValueError as e:
        # Handle the case where the input string is not in the expected format
        print(f"Error: {e}")
        return None