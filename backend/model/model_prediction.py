import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from google.cloud import storage
import os
import tempfile
import requests

def download_model_from_gcs(bucket_name, gcs_model_dir, local_dir):
    base_url = f"https://storage.googleapis.com/{bucket_name}/{gcs_model_dir}"
    files = [
        "config.json",
        "model.safetensors",
        "special_tokens_map.json",
        "tokenizer_config.json",
        "vocab.txt"
    ]

    os.makedirs(local_dir, exist_ok=True)
    for file in files:
        url = f"{base_url}/{file}"
        local_path = os.path.join(local_dir, file)
        print(f"Downloading {url}")
        response = requests.get(url)
        with open(local_path, 'wb') as f:
            f.write(response.content)
        print(f"Saved to {local_path}")

def run_model_prediction(input_text, use_local_model):
    if use_local_model:
        model_path = os.path.join(os.path.dirname(__file__), 'distilbert_media_bias_model_v3')
    else:
        bucket_name = "distilbert-models"
        gcs_model_dir = 'distilbert_media_bias_model_v3'

        tmp_dir = tempfile.TemporaryDirectory()
        local_model_path = tmp_dir.name
        download_model_from_gcs(bucket_name, gcs_model_dir, local_model_path)
        model_path = local_model_path

    tokenizer = DistilBertTokenizer.from_pretrained(model_path)
    model = DistilBertForSequenceClassification.from_pretrained(model_path)
    model.eval()

    print("is device cuda", torch.cuda.is_available())
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    model.to(device)

    inputs = tokenizer(
        input_text,
        return_tensors="pt",
        padding="max_length",
        truncation=True,
        max_length=512
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        predicted_score = outputs.logits.squeeze().item()

    print(f"Predicted bias score: {predicted_score:.2f} (scale: -10 = left, 0 = neutral, +10 = right)")
    return predicted_score