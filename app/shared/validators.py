def validate_required(value, field_name="Field"):
    if not value or (isinstance(value, str) and not value.strip()):
        return f"{field_name} is required"
    return None

def validate_email(email):
    if email and "@" not in email:
        return "Invalid email address"
    return None

def validate_positive_number(value, field_name="Field"):
    try:
        v = float(value)
        if v < 0:
            return f"{field_name} must be positive"
    except (ValueError, TypeError):
        return f"{field_name} must be a number"
    return None
