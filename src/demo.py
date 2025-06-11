from google.cloud import vision

def rgb_to_basic_color(r, g, b):
    """Convert RGB values to basic color names only."""
    if r > 200 and g > 200 and b > 200:
        return "White"
    if r < 50 and g < 50 and b < 50:
        return "Black"
    # Gray scale check
    if abs(r - g) < 30 and abs(r - b) < 30 and abs(g - b) < 30:
        return "Gray"
    max_val = max(r, g, b)
    min_val = min(r, g, b)
    if max_val == r:
        if g > 150 and b < 100:
            return "Orange"
        return "Red"
    if max_val == g:
        if r > 150 and b < 100:
            return "Yellow"
        return "Green"
    if max_val == b:
        if r > 150 and g > 150:
            return "Cyan"
        if r > 150:
            return "Magenta"
        return "Blue"
    return "Mixed"

def analyze_image(image_path, credentials_path):
    # Initialize the client
    client = vision.ImageAnnotatorClient.from_service_account_json(credentials_path)
    # Read the image file
    with open(image_path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)

    # 1. Get color properties (already sorted by score)
    color_response = client.image_properties(image=image)
    colors = color_response.image_properties_annotation.dominant_colors.colors
    if colors:
        dominant_color = colors[0].color
        r, g, b = int(dominant_color.red), int(dominant_color.green), int(dominant_color.blue)
        color_name = rgb_to_basic_color(r, g, b)
        color_str = f"{color_name}"
    else:
        color_str = "No dominant color detected"

    # 2. Get label annotations (take the label with highest topicality)
    label_response = client.label_detection(image=image)
    labels = label_response.label_annotations
    if labels:
        # Find label with highest topicality
        best_label = max(labels, key=lambda x: x.topicality)
        label_str = f"{best_label.description}"
    else:
        label_str = "No label detected"

    # 3. Get text detection (OCR, no score, take first as before)
    text_response = client.text_detection(image=image)
    texts = text_response.text_annotations
    if texts:
        #comment after strip() to get all text instead of first word
        detected_text = texts[0].description.strip().split('\n')[0]
        text_str = f"{detected_text}"
    else:
        text_str = "No text detected"

    # Combine all results
    combined_result = f"{text_str} - {color_str} - {label_str}"
    return combined_result

if __name__ == "__main__":
    credentials_path = 'secret.json'
    image_path = 'img1.png'
    try:
        result = analyze_image(image_path, credentials_path)
        print("Analysis Results:")
        print(result)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
