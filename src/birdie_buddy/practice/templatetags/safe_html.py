import bleach
import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

# Define allowed HTML tags and attributes for markdown content
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'i', 'b',
    'ul', 'ol', 'li',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'span', 'a', 'code', 'pre', 'blockquote', 'hr'
]

ALLOWED_ATTRIBUTES = {
    '*': ['class'],
    'a': ['href', 'title'],
}


@register.filter
def safe_html(value):
    """
    Convert markdown to HTML and sanitize it.
    Safe for displaying user-generated markdown content.
    """
    if not value:
        return ''
    
    # Convert markdown to HTML
    html = markdown.markdown(
        value,
        extensions=['nl2br'],  # Convert newlines to <br> tags
        output_format='html'
    )
    
    # Clean the HTML to remove potentially dangerous content
    clean_html = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )
    
    return mark_safe(clean_html)
