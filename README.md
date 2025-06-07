
# Google Cloud Vision API - Cheatsheet

Ce guide explique comment configurer et utiliser le script Python qui exploite l’API Google Cloud Vision pour analyser une image et détecter sa couleur dominante, ses labels, et son texte (OCR).

---

## Prérequis

- Un compte Google Cloud Platform (GCP)
- Python 3.x installé sur votre machine
- Accès à Internet

---

## Étapes pour configurer et utiliser le script

### 1. Créer un projet Google Cloud

- Connectez-vous à la console Google Cloud : https://console.cloud.google.com/
- Cliquez sur **"Select a project"** puis **"New Project"**
- Donnez un nom à votre projet (ex : `vision-poc`)
- Cliquez sur **"Create"**

### 2. Activer la facturation

- Dans la console GCP, allez dans **"Billing"** (Facturation)
- Associez un compte de facturation à votre projet
- Note : Google offre un crédit gratuit à l’inscription, ce qui permet de tester l’API sans frais initialement.

### 3. Activer l’API Vision

- Dans la console GCP, allez dans **"API & Services" > "Library"**
- Recherchez **"Cloud Vision API"**
- Cliquez sur **"Enable"** (Activer)

### 4. Créer et télécharger les identifiants (clé de service)

- Allez dans **"API & Services" > "Credentials"**
- Cliquez sur **"Create Credentials" > "Service account"**
- Donnez un nom au compte de service (ex : `vision-poc-sa`)
- Attribuez le rôle **"Project > Editor"** (ou plus restrictif selon besoin)
- Créez la clé en sélectionnant **JSON**
- Téléchargez le fichier JSON (ex : `secret.json`)
- Placez ce fichier dans le dossier où vous exécuterez le script Python

### 5. Installer les bibliothèques Python nécessaires

Ouvrez un terminal (cmd, bash, etc.) et lancez :

```bash
pip install google-cloud-vision
```

### 6. Préparer votre image

- Placez l’image à analyser (ex : `img1.png`) dans le même dossier que votre script Python ou indiquez le chemin complet dans la variable `image_path` du script.

---

## Utilisation du script Python

Voici un rappel rapide du fonctionnement du script `analyze_image` :

- Il charge la clé de service depuis `secret.json`
- Il charge l’image à analyser depuis `img1.png`
- Il appelle 3 fonctionnalités de l’API Vision :
  - Détection des couleurs dominantes
  - Détection des labels (tags)
  - Détection de texte (OCR)
- Il renvoie une chaîne combinée avec la couleur dominante, le label principal, et le texte détecté
- Pour une meilleure lecture de la couleur, le script convertit les valeurs RGB en une couleur de base (par exemple, "Red", "Green", "Blue", etc.)

---

## Exemple d'exécution

Placez-vous dans le dossier contenant `demo.py`, `secret.json` et `img1.png`, puis lancez :

```bash
python demo.py
```

Vous devriez voir s’afficher quelque chose comme :

```
Analysis Results:
PUMA - Green - Active Shirt
```

---

## Code complet du script

```python
from google.cloud import vision

def rgb_to_basic_color(r, g, b):
    if r > 200 and g > 200 and b > 200:
        return "White"
    if r < 50 and g < 50 and b < 50:
        return "Black"
    if abs(r - g) < 30 and abs(r - b) < 30 and abs(g - b) < 30:
        return "Gray"
    max_val = max(r, g, b)
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
    client = vision.ImageAnnotatorClient.from_service_account_json(credentials_path)
    with open(image_path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    color_response = client.image_properties(image=image)
    colors = color_response.image_properties_annotation.dominant_colors.colors
    if colors:
        dominant_color = colors[0].color
        r, g, b = int(dominant_color.red), int(dominant_color.green), int(dominant_color.blue)
        color_name = rgb_to_basic_color(r, g, b)
        color_str = f"{color_name}"
    else:
        color_str = "No dominant color detected"
    label_response = client.label_detection(image=image)
    labels = label_response.label_annotations
    if labels:
        top_label = labels[0].description
        label_str = f"{top_label}"
    else:
        label_str = "No label detected"
    text_response = client.text_detection(image=image)
    texts = text_response.text_annotations
    if texts:
        detected_text = texts[0].description.strip().split('\n')[0]
        text_str = f"{detected_text}"
    else:
        text_str = "No text detected"
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
```

---

## Remarques

- Le fichier JSON contient des informations sensibles : ne le partagez pas publiquement.
- Vous pouvez modifier `credentials_path` et `image_path` pour tester avec d’autres images et clés.