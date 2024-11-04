from datetime import date

def calculate_amount(property_id=None, start_date=None, end_date=None):
    if property_id is not None:
        # Implement logic to get the property price based on property_id
        property_price = 1000  # Example fixed price for demonstration
        return property_price

    if start_date is not None and end_date is not None:
        # Example logic to calculate total price based on date range
        property_price_per_night = 100  # Example price per night
        duration = (end_date - start_date).days
        if duration < 0:
            raise ValueError("End date must be after start date.")
        return duration * property_price_per_night

    raise ValueError("Either property_id or both start_date and end_date must be provided.")
