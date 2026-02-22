"""Simple matcher module for the Wizard-of-Oz prototype.

This file contains a small `WIZARD_MAP` and helper functions that
simulate analysis and return pre-canned matches. Keep logic here so
`app.py` remains UI-only.
"""
import os
import json
import base64


def get_ai_style_read(image_bytes: bytes, api_key: str) -> str:
    """Send the uploaded image to GPT-4o and return a short style description."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "You are a fashion stylist. In 2–3 sentences, describe the "
                                "aesthetic, silhouette, colour palette, and overall vibe of "
                                "this outfit or mood board image. Be specific and style-forward."
                            ),
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                        },
                    ],
                }
            ],
            max_tokens=120,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Style read unavailable: {e}"

# Map demo inspiration filename -> list of marketplace image paths
WIZARD_MAP = {
	"inspo1.jpeg": ["data/matches/inspo1_1.jpg", "data/matches/inspo1_2.jpg"],
	"inspo2.jpeg": ["data/matches/inspo2_1.jpg", "data/matches/inspo2_2.jpg"],
	"inspo3.jpeg": ["data/matches/inspo3_1.jpg", "data/matches/inspo3_2.jpg"],
}

def list_demo_inspirations(folder="data/inspiration"):
	if not os.path.isdir(folder):
		return []
	return sorted([f for f in os.listdir(folder) if f.lower().endswith((".jpg", ".jpeg", ".png"))])

ANALYSIS_MAP = {
	"inspo1.jpeg": {"Full-length": 0.6, "Earth Tones": 0.8, "Relaxed Fit": 0.7},
	"inspo2.jpeg": {"Knit": 0.9, "Colourful": 0.85, "Maxi Length": 0.7},
	"inspo3.jpeg": {"Suede": 0.8, "Neutral Tones": 0.75, "Chunky Sole": 0.6},
}

def simulate_analysis(filename_or_bytes):
	"""Return a simulated attribute/confidence dict for UI display.

	`filename_or_bytes` can be a name or an uploaded file-like object.
	"""
	return ANALYSIS_MAP.get(filename_or_bytes, {"Style": 0.5})

def get_matches_for_filename(filename):
	"""Return the list of match image paths for a demo filename.

	If no mapping exists, return an empty list.
	"""
	return WIZARD_MAP.get(filename, [])


def load_matches_for(filename):
	"""Load structured match metadata for `filename` from data/matches/<base>.json.

	If the JSON file is present, it should contain a list of objects with keys:
	`img` (url or local path), `url` (marketplace link), `title`, `price`, `source`.

	If the JSON file is missing, fall back to `WIZARD_MAP` and return list of dicts
	with `img` populated and other fields empty.
	"""
	if not filename:
		return []
	base = os.path.splitext(filename)[0]
	json_path = os.path.join("data", "matches", f"{base}.json")
	if os.path.exists(json_path):
		try:
			with open(json_path, "r", encoding="utf8") as fh:
				data = json.load(fh)
				if isinstance(data, list):
					return data
		except Exception:
			return []

	# fallback to WIZARD_MAP entries (local image paths)
	imgs = WIZARD_MAP.get(filename, [])
	return [{"img": p, "url": "", "title": os.path.basename(p), "price": "", "source": ""} for p in imgs]

