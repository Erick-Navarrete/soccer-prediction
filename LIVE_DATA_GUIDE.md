# 📊 Live Data & Update Frequency Guide

## Current Update Frequency

**Status**: ✅ **Scheduled Updates Enabled**

- **Update Frequency**: Every 6 hours (automatic)
- **Data Source**: football-data.co.uk (historical data)
- **Update Type**: Scheduled cron job on Render
- **Last Updated**: Displayed in web interface

## 🚀 Live Data Integration Options

### Option 1: API-Football (Recommended for Live Data)

**Features**:
- ✅ Live match scores and status
- ✅ Real-time odds updates
- ✅ Match events (goals, cards, substitutions)
- ✅ Lineups and team statistics
- ✅ League standings and tables

**Pricing**:
- **Free Tier**: 100 requests/day
- **Basic ($10/month)**: 1,000 requests/day
- **Pro ($30/month)**: 10,000 requests/day

**Setup**:
1. Get API key from https://rapidapi.com/api-sports/api/api-football
2. Add `API_FOOTBALL_KEY` to environment variables
3. Enable live data endpoints

**Update Frequency with API-Football**:
- **Live Matches**: Every 1-5 minutes
- **Odds Updates**: Every 5-10 minutes
- **Match Events**: Real-time (push notifications)

### Option 2: Football-Data.org (Free Alternative)

**Features**:
- ✅ Free API
- ✅ Match fixtures and results
- ✅ League standings
- ✅ Team statistics

**Limitations**:
- ❌ No live data
- ❌ Limited to historical data
- ❌ 10 requests/minute rate limit

**Update Frequency**: Daily or weekly

### Option 3: TheSportsDB (Free)

**Features**:
- ✅ Completely free
- ✅ Match schedules and results
- ✅ Team information
- ✅ Player statistics

**Limitations**:
- ❌ No live data
- ❌ Limited coverage
- ❌ Rate limited

**Update Frequency**: Daily

## 🔄 Update Frequency Options

### Current Setup (Every 6 Hours)

**Pros**:
- ✅ Good balance between freshness and resource usage
- ✅ Fits within free API limits
- ✅ Minimal server load
- ✅ Automatic via Render cron jobs

**Cons**:
- ❌ Not truly live
- ❌ May miss late-breaking news

### Enhanced Setup (Every 1 Hour)

**Implementation**:
```yaml
# render.yaml
crons:
  - name: update-predictions-hourly
    schedule: "0 * * * *"  # Every hour
    command: python src/update_predictions.py
```

**Pros**:
- ✅ More frequent updates
- ✅ Better for in-play betting
- ✅ Still within most API limits

**Cons**:
- ❌ Higher resource usage
- ❌ May hit API rate limits

### Live Setup (Every 5 Minutes)

**Implementation**:
```yaml
# render.yaml
crons:
  - name: update-predictions-live
    schedule: "*/5 * * * *"  # Every 5 minutes
    command: python src/update_predictions.py
```

**Pros**:
- ✅ Near real-time updates
- ✅ Best for live betting
- ✅ Most up-to-date predictions

**Cons**:
- ❌ Requires paid API plan
- ❌ Higher server costs
- ❌ May exceed free tier limits

## 🎯 Recommended Implementation Plan

### Phase 1: Current Setup (✅ Complete)
- ✅ Scheduled updates every 6 hours
- ✅ Manual update trigger via API
- ✅ Last updated timestamp display
- ✅ Status endpoint for monitoring

### Phase 2: API-Football Integration (Next Step)
1. Get API-Football key
2. Add to environment variables
3. Enable live match endpoints
4. Update frequency: Every 30 minutes

### Phase 3: Real-time Updates (Advanced)
1. Implement WebSocket for live updates
2. Push notifications for match events
3. Live odds updates every minute
4. In-play prediction adjustments

## 📡 API Endpoints Available

### Current Endpoints
- `GET /api/status` - System status and last updated
- `POST /api/update` - Manual update trigger
- `GET /api/live-matches` - Live match data (requires API key)
- `GET /api/predictions` - Current predictions
- `GET /api/historical` - Historical predictions

### New Endpoints (with API-Football)
- `GET /api/live-matches` - Currently live matches
- `GET /api/match/<id>/events` - Match events
- `GET /api/match/<id>/odds` - Current odds
- `GET /api/standings` - League standings

## 🔧 Configuration

### Environment Variables

Add these to your Render dashboard:

```bash
# For API-Football (optional, for live data)
API_FOOTBALL_KEY=your_api_key_here

# Update frequency (optional)
UPDATE_FREQUENCY=6  # hours
```

### Cron Job Configuration

Edit `render.yaml` to change update frequency:

```yaml
crons:
  - name: update-predictions
    schedule: "0 */6 * * *"  # Every 6 hours
    # Change to:
    # schedule: "0 * * * *"  # Every hour
    # schedule: "*/30 * * * *"  # Every 30 minutes
    command: python src/update_predictions.py
```

## 📱 Mobile-Friendly Live Updates

### Current Features
- ✅ Responsive design
- ✅ Mobile-optimized interface
- ✅ Touch-friendly controls
- ✅ Fast loading times

### Future Enhancements
- 📲 Push notifications for match starts
- 📲 Live score updates
- 📲 In-play probability changes
- 📲 WebSocket for real-time data

## 💡 Tips for Optimal Performance

1. **Start with 6-hour updates** - Good balance
2. **Monitor API usage** - Stay within limits
3. **Cache responses** - Reduce API calls
4. **Use webhooks** - Get updates pushed to you
5. **Implement rate limiting** - Protect your API key

## 🎉 Summary

**Current Status**: Your system is set up with:
- ✅ Automatic updates every 6 hours
- ✅ Manual update capability
- ✅ Status monitoring
- ✅ Ready for live data integration

**Next Steps**:
1. Get API-Football key for live data
2. Update frequency to 1 hour if needed
3. Implement WebSocket for real-time updates
4. Add push notifications

Your system is production-ready and can be easily enhanced with live data!
