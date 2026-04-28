# Soccer Prediction Web Interface

A mobile-friendly web application for viewing soccer match predictions with real-time updates and interactive visualizations.

## Features

- **Live Predictions**: View upcoming match predictions with confidence scores
- **Team Rankings**: ELO-based team rankings
- **Performance Metrics**: Model accuracy and statistics
- **Mobile Responsive**: Optimized for all screen sizes
- **Real-time Updates**: Auto-refresh every minute
- **Interactive UI**: Click on matches for detailed information

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Pipeline First

The web application requires trained model and data. Run the main pipeline:

```bash
cd ..
python src/main.py
```

This will generate:
- `outputs/ensemble_model.pkl` - Trained model
- `outputs/scaler.pkl` - Feature scaler
- `outputs/latest_data.csv` - Latest match data

### 3. Start the Web Server

```bash
cd web
python app.py
```

The application will be available at: http://localhost:5000

## Usage

### Viewing Predictions

1. Open http://localhost:5000 in your browser
2. Navigate between tabs:
   - **Predictions**: View upcoming match predictions
   - **Top Teams**: ELO-based team rankings
   - **Performance**: Model accuracy metrics

### Match Details

Click on any prediction card to see detailed information:
- ELO ratings for both teams
- Probability breakdown (Home/Draw/Away)
- Confidence score
- Match metadata

### Refreshing Data

Click the "Refresh" button to update predictions with the latest data.

## API Endpoints

### GET /api/predictions
Get all upcoming predictions.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "date": "2024-05-01 15:00",
      "home_team": "Arsenal",
      "away_team": "Chelsea",
      "league": "Premier League",
      "prediction": "Home Win",
      "confidence": 65.5,
      "home_prob": 65.5,
      "draw_prob": 20.0,
      "away_prob": 14.5,
      "home_elo": 1650,
      "away_elo": 1580,
      "elo_diff": 70
    }
  ],
  "count": 20,
  "last_updated": "2024-04-28 18:00:00"
}
```

### GET /api/teams
Get top teams by ELO rating.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "rank": 1,
      "team": "Manchester City",
      "elo": 1750
    }
  ]
}
```

### GET /api/performance
Get model performance metrics.

**Response:**
```json
{
  "success": true,
  "data": {
    "accuracy": 56.5,
    "log_loss": 0.86,
    "total_predictions": 1250,
    "last_updated": "2024-04-28"
  }
}
```

### GET /api/match/{id}
Get detailed information for a specific match.

### GET /api/refresh
Trigger a data refresh.

## Configuration

### Port

By default, the app runs on port 5000. To change:

```python
# In app.py
app.run(debug=True, host='0.0.0.0', port=8080)  # Change port
```

### Host

To make the app accessible from other devices:

```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

## Deployment

### Local Network

1. Find your local IP:
```bash
ipconfig  # Windows
ifconfig  # Linux/Mac
```

2. Run with host='0.0.0.0':
```bash
python app.py
```

3. Access from other devices: `http://YOUR_IP:5000`

### Cloud Deployment

#### Heroku

1. Create `Procfile`:
```
web: python web/app.py
```

2. Deploy:
```bash
heroku create your-app-name
git push heroku main
```

#### PythonAnywhere

1. Upload files to PythonAnywhere
2. Configure WSGI file
3. Set up virtual environment
4. Install dependencies
5. Run web app

#### Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "web/app.py"]
```

Build and run:
```bash
docker build -t soccer-predictions .
docker run -p 5000:5000 soccer-predictions
```

## Troubleshooting

### "No trained model found"

**Solution**: Run the main pipeline first:
```bash
python src/main.py
```

### "No data found"

**Solution**: Ensure the pipeline completed successfully and check `outputs/latest_data.csv`

### Port already in use

**Solution**: Change the port in `app.py` or kill the process using the port:
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill
```

### CORS errors (if accessing from different domain)

**Solution**: Add CORS support to Flask:
```python
from flask_cors import CORS
CORS(app)
```

## Development

### Adding New Features

1. Add API endpoint in `app.py`
2. Update frontend in `templates/index.html`
3. Add styling in `static/css/style.css`
4. Add JavaScript logic in `static/js/app.js`

### Testing

Test API endpoints:
```bash
curl http://localhost:5000/api/predictions
curl http://localhost:5000/api/teams
curl http://localhost:5000/api/performance
```

## Performance Optimization

- Enable caching for API responses
- Use pagination for large datasets
- Implement WebSocket for real-time updates
- Add CDN for static assets

## Security

- Add authentication for admin features
- Implement rate limiting
- Use HTTPS in production
- Sanitize user inputs
- Keep dependencies updated

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## License

MIT License - See main project LICENSE file for details.
