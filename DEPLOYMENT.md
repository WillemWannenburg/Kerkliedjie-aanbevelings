# Kerkliedaanbeveler - Deployment Guide

## Streamlit Cloud Deployment

### Prerequisites
1. GitHub account
2. Streamlit Cloud account (free at https://streamlit.io/cloud)

### Steps to Deploy

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Convert to Streamlit app"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to https://streamlit.io/cloud
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set the main file path to: `recommend_songs.py`
   - Click "Deploy"

### File Structure Required
```
church-songs-recommender/
├── recommend_songs.py          # Main Streamlit app
├── combined_songs.json         # Songs data (required)
├── requirements.txt            # Python dependencies
├── .streamlit/
│   └── config.toml            # Streamlit configuration
└── DEPLOYMENT.md              # This file
```

### Important Notes

1. **Data File**: Make sure `combined_songs.json` is included in your repository
2. **Dependencies**: All required packages are listed in `requirements.txt`
3. **Model Download**: The AI model will be downloaded automatically on first run
4. **Caching**: The app uses Streamlit caching for better performance

### Local Testing

To test locally before deployment:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run recommend_songs.py
```

### Troubleshooting

- **Model loading issues**: Check internet connection for model download
- **Data loading issues**: Ensure `combined_songs.json` exists and is valid JSON
- **Memory issues**: The app uses caching to reduce memory usage

### Features

- ✅ Afrikaans interface
- ✅ AI-powered song recommendations
- ✅ Beautiful UI with custom styling
- ✅ Responsive design
- ✅ Error handling and user feedback
- ✅ Caching for better performance
