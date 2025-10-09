# Crypto Calculator Backend

A Django REST API backend for cryptocurrency analysis and calculation, providing real-time data processing, technical analysis, and market sentiment evaluation.

## Overview

This backend service provides comprehensive cryptocurrency analysis capabilities including:
- Real-time OHLCV (Open, High, Low, Close, Volume) data management
- Technical indicators (Moving Averages, RSI)
- Market sentiment analysis
- Multi-currency pair support
- Automated database updates from CryptoCompare API

## Features

### Core Functionality
- **OHLCV Data Management**: Store and retrieve historical cryptocurrency price data
- **Currency Pair Support**: Handle multiple crypto/fiat trading pairs (BTC/USD, ETH/GBP, etc.)
- **Real-time Updates**: Automatic database synchronization with external APIs
- **Technical Analysis**: Moving averages and RSI calculations
- **Market Sentiment**: News sentiment analysis for market insights

### API Endpoints

#### System Status
- `GET /api/get_system_status/` - Check service health

#### Data Management
- `PUT /api/update_database/?pair=BTC/USD` - Update database with latest data
- `GET /api/pair_data/?pair=BTC/USD&from_ts=<timestamp>&to_ts=<timestamp>` - Get price data for time range

#### Currency Information
- `GET /api/available_currencies/` - List all supported crypto and fiat currencies
- `GET /api/available_analyses/` - List all available analysis types

#### Technical Analysis
- `GET /api/moving_average/?pair=BTC/USD&from_ts=<timestamp>&to_ts=<timestamp>&day_ma=7` - Calculate moving averages
- `GET /api/rsi/?pair=BTC/USD&from_ts=<timestamp>&to_ts=<timestamp>` - Calculate RSI values

#### Market Analysis
- `GET /api/market_sentiment/?search_string=Bitcoin` - Get sentiment analysis for search terms

## Technology Stack

### Core Framework
- **Django 5.2.3**: Web framework
- **Django REST Framework 3.16.0**: API development
- **PostgreSQL**: Primary database (with psycopg2-binary)
- **Gunicorn**: WSGI HTTP Server

### Data Processing
- **Pandas 2.3.0**: Data manipulation and analysis
- **NumPy 2.3.1**: Numerical computing
- **Matplotlib 3.10.3**: Data visualization

### External APIs & Scraping
- **Requests 2.32.4**: HTTP client for API calls
- **BeautifulSoup4 4.13.5**: Web scraping
- **Playwright 1.55.0**: Browser automation

### Natural Language Processing
- **NLTK 3.9.1**: Natural language processing
- **TextBlob 0.19.0**: Sentiment analysis
- **Loguru 0.7.3**: Advanced logging

### Testing & Development
- **Pytest 8.4.2**: Testing framework
- **Django Extensions 4.1**: Development utilities

## Project Structure

```
crypto_calc_backend/
├── server/                    # Django project root
│   ├── api/                   # Main API application
│   │   ├── models.py         # Database models (OHLCV, CurrencyPair)
│   │   ├── views.py          # API endpoints and business logic
│   │   ├── serializers.py    # DRF serializers
│   │   ├── urls.py           # URL routing
│   │   └── CoinDeskAPI/      # External API integration
│   │       └── API.py        # CryptoCompare API client
│   ├── server/               # Django settings
│   │   ├── settings.py       # Configuration
│   │   ├── urls.py          # Root URL configuration
│   │   └── wsgi.py          # WSGI application
│   └── tests/               # Test suite
│       ├── API_test.py      # API integration tests
│       └── test_api_endpoints.py  # Endpoint tests
├── Dockerfile               # Container configuration
├── requirements.txt         # Python dependencies
├── startup.sh              # Container startup script
└── README.md              # This file
```

## Database Models

### CurrencyPair
```python
class CurrencyPair(models.Model):
    base_code = models.CharField(max_length=10)   # e.g., BTC
    quote_code = models.CharField(max_length=10)  # e.g., USD
```

### OHLCV
```python
class OHLCV(models.Model):
    pair = models.ForeignKey(CurrencyPair, on_delete=models.CASCADE)
    timestamp = models.BigIntegerField()
    open = models.DecimalField(max_digits=18, decimal_places=3)
    high = models.DecimalField(max_digits=18, decimal_places=3)
    low = models.DecimalField(max_digits=18, decimal_places=3)
    close = models.DecimalField(max_digits=18, decimal_places=3)
    volumeFrom = models.DecimalField(max_digits=30, decimal_places=3)
    volumeTo = models.DecimalField(max_digits=30, decimal_places=3)
```

## API Usage Examples

### Get System Status
```bash
curl http://localhost:8000/api/get_system_status/
```

### Update Database
```bash
curl -X PUT "http://localhost:8000/api/update_database/?pair=BTC/USD"
```

### Get Price Data
```bash
curl "http://localhost:8000/api/pair_data/?pair=BTC/USD&from_ts=1640995200&to_ts=1641081600"
```

### Calculate Moving Average
```bash
curl "http://localhost:8000/api/moving_average/?pair=BTC/USD&from_ts=1640995200&to_ts=1641081600&day_ma=7"
```

### Get Market Sentiment
```bash
curl "http://localhost:8000/api/market_sentiment/?search_string=Bitcoin"
```

## Configuration

### Environment Variables
- `DB_HOST`: Database host (default: localhost)
- `DB_PORT`: Database port (default: 5432)
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password
- `DB_NAME`: Database name
- `COIN_DESK_API_KEY`: CryptoCompare API key

### Supported Currency Pairs
**Cryptocurrencies**: BTC, ETH, SOL, SUI
**Fiat Currencies**: USD, GBP, EUR

## Development Setup

### Local Development
1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Database Migration**:
   ```bash
   cd server
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Run Development Server**:
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

### Docker Development
```bash
docker build -t crypto-calc-backend .
docker run -p 8000:8000 crypto-calc-backend
```

## Technical Analysis Features

### Moving Averages
- Configurable time windows (hourly/daily)
- Pandas-based rolling calculations
- Support for custom periods

### RSI (Relative Strength Index)
- 14-period default with custom period support
- Standard RSI calculation methodology
- Hourly data point processing

### Market Sentiment Analysis
- Real-time news sentiment scoring
- CoinDesk news API integration
- Sentiment aggregation and scoring

## Performance Optimization

### Database Optimization
- Compound indexes on (pair, timestamp) for fast queries
- Bulk operations for API data ingestion
- Efficient queryset filtering and ordering

### API Rate Limiting
- CryptoCompare API rate limit handling (2000 requests/hour)
- Intelligent batch processing for large data updates
- Automatic retry logic with exponential backoff

## Testing

Run the test suite:
```bash
cd server
python -m pytest tests/ -v
```

## Production Deployment

### Gunicorn Configuration
```bash
gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 server.wsgi:application
```

### Health Checks
The API provides a health check endpoint at `/api/get_system_status/` for monitoring and load balancer integration.

## Contributing

1. Follow Django best practices
2. Add tests for new features
3. Update API documentation
4. Use type hints where appropriate
5. Maintain backward compatibility

## License

This project is part of the larger crypto_calc application suite.