#!/usr/bin/env python3
"""Test script to fetch available models from NanoGPT API"""
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

print(f"API Key (first 10 chars): {api_key[:10]}...")

# Fetch models
headers = {
    "Authorization": f"Bearer {api_key}",
}

print("\nFetching models from NanoGPT API...")
response = requests.get("https://nano-gpt.com/api/v1/models", headers=headers)

print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    models = data.get("data", [])
    print(f"\nFound {len(models)} models\n")
    
    # Print model IDs and owners
    print("Available models:")
    print("-" * 80)
    for model in models[:50]:  # Show first 50
        model_id = model.get("id", "")
        owner = model.get("owned_by", "")
        print(f"{model_id:<50} (owner: {owner})")
    
    if len(models) > 50:
        print(f"\n... and {len(models) - 50} more models")
    
    # Filter for some popular ones
    print("\n" + "="*80)
    print("RECOMMENDED MODELS FOR DABSTEP:")
    print("="*80)
    
    keywords = ["gpt-4o", "claude-3", "deepseek", "qwen", "gemini"]
    recommended = []
    for model in models:
        model_id = model["id"]
        if any(keyword in model_id.lower() for keyword in keywords):
            recommended.append(model_id)
    
    for model_id in sorted(recommended):
        print(f"  {model_id}")
        
else:
    print(f"Error: {response.text}")
