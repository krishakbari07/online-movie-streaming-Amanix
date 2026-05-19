from django import template

register = template.Library()

@register.filter
def get_star_id(star_name, star_objects):
    """Get star_id from star_objects dictionary. Try both original and lowercase."""
    if not star_objects or not star_name:
        return None
    
    # exact match first
    if star_name in star_objects:
        return star_objects[star_name]
    
    #  lowercase match
    star_name_lower = star_name.lower()
    if star_name_lower in star_objects:
        return star_objects[star_name_lower]
    
    return None

@register.filter
def has_star_link(star_name, star_objects):
    """Check if star_name exists in star_objects."""
    if not star_objects or not star_name:
        return False
    
    # exact match first
    if star_name in star_objects:
        return True
    
    # lowercase match
    if star_name.lower() in star_objects:
        return True
    
    return False

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary by key."""
    try:
        if dictionary and key in dictionary:
            return dictionary[key]
    except (TypeError, AttributeError):
        pass
    return None

