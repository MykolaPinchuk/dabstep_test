#!/usr/bin/env python3
"""Fetch OSS (open-source) models from NanoGPT API"""
import requests
import json
import os
import re

# Load NanoGPT API key
nanogpt_path = os.path.join(os.path.dirname(__file__), "secrets", "nanogpt_credentials.txt")
with open(nanogpt_path, "r") as f:
    content = f.read()

# Extract API key
key_match = re.search(r"api_key\s*=\s*['\"]([^'\"]+)['\"]", content)
if key_match:
    api_key = key_match.group(1)
else:
    key_match = re.search(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", content)
    api_key = key_match.group(0)

# Fetch models
headers = {"Authorization": f"Bearer {api_key}"}
response = requests.get("https://nano-gpt.com/api/v1/models?detailed=true", headers=headers)

if response.status_code == 200:
    data = response.json()
    models = data.get("data", [])
    
    # Filter for OSS models (free ones based on pricing or name patterns)
    oss_models = []
    
    # Known OSS model patterns and providers
    oss_patterns = [
        "qwen", "deepseek", "llama", "mistral", "gemma", "phi", "mixtral",
        "yi", "solar", "openchat", "wizardlm", "nous", "dolphin", "neural",
        "eva", "cognitivecomputations", "huihui-ai", "undi95", "gryphe",
        "sao10k", "nousresearch", "teknium", "intel", "google", "meta-llama"
    ]
    
    # Exclude proprietary models
    exclude_patterns = [
        "gpt-4", "gpt-5", "claude", "o1", "o3", "gemini-1.5-pro", 
        "chatgpt", "azure", "study_gpt", "auto-model", "sonar"
    ]
    
    for model in models:
        model_id = model.get("id", "")
        owner = model.get("owned_by", "")
        pricing = model.get("pricing", {})
        
        # Check if model matches OSS patterns
        is_oss = any(pattern in model_id.lower() for pattern in oss_patterns)
        is_excluded = any(pattern in model_id.lower() for pattern in exclude_patterns)
        
        # Also check if it's free based on pricing
        prompt_cost = pricing.get("prompt", 999) if pricing else 999
        is_free = prompt_cost == 0 or prompt_cost is None
        
        if (is_oss or is_free) and not is_excluded:
            name = model.get("name", "")
            context = model.get("context_length", "?")
            oss_models.append({
                "id": model_id,
                "name": name,
                "owner": owner,
                "context": context,
                "pricing": pricing
            })
    
    print(f"Found {len(oss_models)} OSS/Free models\n")
    print("="*100)
    print("OSS MODELS FOR NANOGPT (Copy to notebook):")
    print("="*100)
    
    # Sort by owner then by name
    oss_models.sort(key=lambda x: (x['owner'], x['id']))
    
    # Print in Python dict format, limit to ~60 models
    print("\nMODELS_NANOGPT = {")
    
    count = 0
    for model in oss_models[:70]:  # Get first 70
        model_id = model['id']
        # Create a friendly key name
        key = model_id.replace("/", "-").replace("_", "-").replace(".", "-").lower()
        # Shorten very long keys
        if len(key) > 45:
            parts = key.split("-")
            key = "-".join(parts[-3:]) if len(parts) > 3 else key[:45]
        
        print(f'    "{key}": "{model_id}",')
        count += 1
    
    print("}")
    print(f"\n{count} models listed")
    
else:
    print(f"Error: {response.status_code} - {response.text}")
