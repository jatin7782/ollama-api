# Ollama AI Website

Static GitHub Pages frontend + FastAPI backend + Ollama.

## 1. Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

## 2. Download the model

```bash
ollama pull qwen2.5-coder:1.5b
```

## 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

## 4. Start the API

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 5. Forward port 8000

Make port 8000 public in GitHub Codespaces.

## 6. Configure the website

Edit `script.js`:

```js
const API_URL = "https://YOUR-CODESPACE-URL.app.github.dev";
```

## 7. GitHub Pages

Enable:

Settings → Pages → Deploy from branch → main → root

Important: the Codespace must be running for the AI backend to work.
