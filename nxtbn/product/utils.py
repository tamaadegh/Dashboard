import json


def json_to_html(json_data):
    try:
        data = json.loads(json_data)
    except json.JSONDecodeError as e:
        return f"<!-- Invalid JSON: {e} -->"

    html = []

    for element in data:
        try:
            element_type = element.get("type")
            children = element.get("children", [])

            if element_type == "paragraph":
                align = element.get("align", "")
                align_attr = f' style="text-align: {align};"' if align else ""
                html.append(f'<p{align_attr}>' + process_children(children) + "</p>")

            elif element_type == "h1":
                html.append("<h1>" + process_children(children) + "</h1>")

            elif element_type == "code":
                html.append("<pre><code>" + process_children(children) + "</code></pre>")

            elif element_type == "link":
                url = element.get("url", "#")
                html.append(f'<a href="{sanitize_url(url)}">' + process_children(children) + "</a>")

            elif element_type == "image":
                url = element.get("url", "")
                alt = element.get("alt", "Image")
                html.append(f'<img src="{sanitize_url(url)}" alt="{sanitize_text(alt)}">')

            else:
                # Handle unsupported or missing types gracefully
                html.append(f"<!-- Unsupported type: {element_type} -->")
        except Exception as e:
            html.append(f"<!-- Error processing element: {e} -->")

    return "".join(html)

def process_children(children):
    content = []
    for child in children:
        try:
            text = child.get("text", "")
            bold = child.get("bold", False)
            underline = child.get("underline", False)
            background_color = child.get("backgroundColor", "")
            color = child.get("color", "")

            if background_color:
                text = f'<span style="background-color: {sanitize_color(background_color)};">{text}</span>'
            if color:
                text = f'<span style="color: {sanitize_color(color)};">{text}</span>'
            if bold:
                text = f'<b>{text}</b>'
            if underline:
                text = f'<u>{text}</u>'

            content.append(text)
        except Exception as e:
            content.append(f"<!-- Error processing child: {e} -->")

    return "".join(content)

def sanitize_url(url):
    # Ensures the URL is valid and safe to use
    return url if url.startswith(("http://", "https://")) else "#"

def sanitize_text(text):
    # Escapes unsafe characters in text
    return text.replace("<", "&lt;").replace(">", "&gt;").replace('"', '&quot;').replace("'", '&#39;')

def sanitize_color(color):
    # Ensures the color value is valid (e.g., hex, rgb)
    if color.startswith("#") and len(color) in {4, 7}:
        return color  # Assume valid hex color
    elif color.startswith("rgb") or color.startswith("rgba"):
        return color  # Assume valid rgb/rgba
    return "inherit"  # Fallback to default
