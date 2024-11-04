from django import template
import logging

# Configure logging
logger = logging.getLogger(__name__)

register = template.Library()

@register.filter
def attr(field, value):
    """
    Update the attributes of a form field with the provided value string.

    The value string should be formatted as "key1:value1,key2:value2".
    Example usage: {{ form.field|attr:"class:my-class,placeholder:Enter text" }}
    """
    logger.debug("attr filter applied with value: %s", value)  # Debugging line
    try:
        # Validate input format
        if not isinstance(value, str) or not value:
            logger.error("Invalid input value: %s. Expected format: key1:value1,key2:value2", value)
            return field  # Return the field unmodified

        # Convert value string into a dictionary of attributes
        attrs = {}
        for item in value.split(","):
            try:
                k, v = item.split(":")
                attrs[k.strip()] = v.strip()
            except ValueError:
                logger.warning("Skipping malformed attribute: %s", item)

        # Ensure field has a widget to update attributes
        if hasattr(field, 'widget'):
            field.widget.attrs.update(attrs)
            logger.info("Successfully updated attributes for field: %s", field.label)  # Log successful update
        else:
            logger.warning("Field does not have a widget to update: %s", field.label)
    except Exception as e:
        logger.error("Unexpected error applying attributes: %s. Input value: %s", e, value)

    return field

@register.filter
def get_item(dictionary, key):
    """Retrieve an item from a dictionary using the key."""
    return dictionary.get(key)
