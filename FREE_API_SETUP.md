# 🚀 Free Live Football API Setup Guide

## Quick Setup (5 Minutes)

### Step 1: Get Your Free API Key

1. Go to: https://rapidapi.com/Creativesdev/api/free-api-live-football-data
2. Click "Subscribe" (Free tier)
3. Sign up or log in to RapidAPI
4. Copy your API key

### Step 2: Add API Key to Render

1. Go to your Render dashboard: https://dashboard.render.com/
2. Click on your `soccer-predictions` web service
3. Scroll to "Environment" section
4. Click "Add Environment Variable"
5. Add:
   - **Key**: `FREE_FOOTBALL_API_KEY`
   - **Value**: `your_api_key_here` (paste your key)
6. Click "Save"

### Step 3: Redeploy

1. Click "Manual Deploy" → "Deploy latest commit"
2. Wait 2-3 minutes for deployment
3. Your site will now have live data!

## 🎯 What You Get With This API

### Live Match Data
- ✅ Currently live matches
- ✅ Real-time scores
- ✅ Match status (live, half-time, full-time)
- ✅ Match minute (for live games)

### Upcoming Fixtures
- ✅ Next 7 days of fixtures
- ✅ Match dates and times
- ✅ Team information
- ✅ League details

### Recent Results
- ✅ Last 7 days of results
- ✅ Final scores
- ✅ Match details
- ✅ League information

### League Standings
- ✅ Current league table
- ✅ Points, wins, draws, losses
- ✅ Goal difference
- ✅ Team rankings

## 📡 Available API Endpoints

### Live Matches
```
GET /api/live-matches
```
Returns currently live matches with real-time scores.

### Upcoming Fixtures
```
GET /api/fixtures
```
Returns fixtures for the next 7 days.

### Recent Results
```
GET /api/results
```
Returns results from the last 7 days.

### System Status
```
GET /api/status
```
Returns system status and last updated timestamp.

## 🔧 Testing the API

### Test Locally
```bash
# Set your API key
export FREE_FOOTBALL_API_KEY=your_key_here

# Test the live matches endpoint
curl http://localhost:5000/api/live-matches

# Test fixtures
curl http://localhost:5000/api/fixtures

# Test results
curl http://localhost:5000/api/results
```

### Test on Render
```bash
# Test live matches
curl https://soccer-predictions.onrender.com/api/live-matches

# Test fixtures
curl https://soccer-predictions.onrender.com/api/fixtures

# Test results
curl https://soccer-predictions.onrender.com/api/results
```

## 📊 API Response Format

### Live Matches Response
```json
{
  "success": true,
  "data": [
    {
      "match_id": 123456,
      "home_team": "Manchester United",
      "away_team": "Liverpool",
      "home_score": 2,
      "away_score": 1,
      "status": "In Progress",
      "minute": 67,
      "league": "Premier League",
      "date": "2024-04-28",
      "time": 1714320000
    }
  ],
  "count": 1
}
```

### Fixtures Response
```json
{
  "success": true,
  "data": [
    {
      "match_id": 123457,
      "home_team": "Arsenal",
      "away_team": "Chelsea",
      "league": "Premier League",
      "date": "2024-05-01",
      "time": 1714560000
    }
  ],
  "count": 1
}
```

## 🎨 Frontend Integration

### Display Live Matches
```javascript
// Fetch live matches
fetch('/api/live-matches')
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      data.data.forEach(match => {
        console.log(`${match.home_team} ${match.home_score} - ${match.away_score} ${match.away_team}`);
      });
    }
  });
```

### Display Upcoming Fixtures
```javascript
// Fetch fixtures
fetch('/api/fixtures')
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      data.data.forEach(fixture => {
        console.log(`${fixture.home_team} vs ${fixture.away_team} on ${fixture.date}`);
      });
    }
  });
```

## 🔄 Update Frequency

### Current Setup
- **Live Matches**: Updated on page refresh
- **Fixtures**: Updated every 6 hours (scheduled)
- **Results**: Updated every 6 hours (scheduled)

### Enhanced Setup (Optional)
To get more frequent updates, you can:

1. **Add client-side polling** (every 30 seconds):
```javascript
setInterval(() => {
  fetch('/api/live-matches')
    .then(response => response.json())
    .then(data => updateLiveMatches(data));
}, 30000); // 30 seconds
```

2. **Add WebSocket** (real-time updates):
```javascript
const socket = new WebSocket('wss://your-site.com/live');
socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  updateLiveMatches(data);
};
```

## 🐛 Troubleshooting

### "API key not configured" error
**Solution**: Add `FREE_FOOTBALL_API_KEY` to Render environment variables

### "No live matches found"
**Solution**: This is normal if no matches are currently live. Check during match hours.

### "Rate limit exceeded"
**Solution**: The free API has rate limits. Wait a few minutes before trying again.

### "Invalid API key"
**Solution**: Make sure you copied the correct key from RapidAPI dashboard.

## 💡 Tips

1. **Test during match hours**: Live data is only available during actual matches
2. **Check API status**: Visit RapidAPI dashboard to see if API is operational
3. **Monitor usage**: Check your RapidAPI dashboard for usage statistics
4. **Cache responses**: Implement caching to reduce API calls

## 📈 API Limits

### Free Tier
- **Requests**: Limited (check RapidAPI dashboard)
- **Rate Limit**: Varies by endpoint
- **Features**: All basic features included

### Upgrade Options
If you need more requests, consider upgrading on RapidAPI.

## 🎉 You're Ready!

Once you've added your API key and redeployed, your site will have:

- ✅ Live match scores
- ✅ Upcoming fixtures
- ✅ Recent results
- ✅ Real-time updates

Enjoy your live football data! ⚽
