# DAO Data AI - API Documentation

Comprehensive API documentation for the DAO Data AI platform. This API provides AI-powered governance analytics for DAOs including proposal outcome predictions, sentiment analysis, governance scoring, and real-time alerts.

## 📚 Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
- [Interactive Documentation](#interactive-documentation)
- [API Endpoints](#api-endpoints)
- [Authentication](#authentication)
- [Rate Limiting](#rate-limiting)
- [Error Handling](#error-handling)
- [Examples](#examples)

## 🔍 Overview

The DAO Data AI API is a RESTful API that provides:

- **ML Predictions**: AI-powered predictions for DAO proposal outcomes
- **Sentiment Analysis**: Community sentiment analysis for proposals  
- **Governance Scoring**: Comprehensive governance health scores
- **Real-time Alerts**: Critical governance event monitoring
- **Batch Operations**: Process multiple proposals simultaneously

### Base URLs

- **Production**: `https://dao-data-ai.vercel.app/api`
- **Production (Custom Domain)**: `https://www.sky-mind.com/api`
- **Development**: `http://localhost:8000`

### API Version

Current version: **1.0.0**

## 🚀 Getting Started

### Prerequisites

- No API key required (public access)
- Future versions will implement authentication

### Making Your First Request

```bash
curl https://dao-data-ai.vercel.app/api/advanced/predictions/prop-123
```

### Response Format

All responses are in JSON format:

```json
{
  "proposal_id": "prop-123",
  "prediction": 0.78,
  "confidence": 0.85,
  "model": "RandomForest-v2",
  "features_used": 42,
  "predicted_outcome": "pass"
}
```

## 📖 Interactive Documentation

### Swagger UI

View and test the API interactively using Swagger UI:

**Online Swagger Viewers:**

1. **Swagger Editor**: https://editor.swagger.io/
   - Paste the contents of `openapi.yaml`
   - View documentation and test endpoints

2. **Swagger UI (Online)**: https://petstore.swagger.io/
   - Enter URL: `https://raw.githubusercontent.com/danvolsky-source/dao-data-ai/main/docs/openapi.yaml`
   - Explore the interactive API documentation

### Local Swagger UI Setup

To run Swagger UI locally:

```bash
# Using Docker
docker run -p 8080:8080 \
  -e SWAGGER_JSON=/docs/openapi.yaml \
  -v $(pwd)/docs:/docs \
  swaggerapi/swagger-ui

# Access at http://localhost:8080
```

## 🌐 API Endpoints

### Predictions

#### Get Prediction for a Proposal

```http
GET /advanced/predictions/{proposalId}
```

**Parameters:**
- `proposalId` (path, required): Unique identifier for the proposal

**Response:** `Prediction` object

#### Batch Predictions

```http
POST /advanced/predictions/batch
```

**Request Body:**
```json
{
  "proposalIds": ["prop-123", "prop-456", "prop-789"]
}
```

**Response:**
```json
{
  "predictions": [
    { "proposal_id": "prop-123", "prediction": 0.78, ... },
    { "proposal_id": "prop-456", "prediction": 0.65, ... }
  ]
}
```

### Scores

#### Get Governance Score

```http
GET /advanced/scores/{proposalId}
```

**Parameters:**
- `proposalId` (path, required): Unique identifier for the proposal

**Response:**
```json
{
  "proposal_id": "prop-123",
  "overall_score": 78.5,
  "total_score": 78.5,
  "rating": "GOOD",
  "component_scores": {
    "prediction_confidence": 0.85,
    "sentiment": 0.72,
    "onchain_score": 0.90,
    "social_score": 0.65,
    "technical_score": 0.88
  }
}
```

### Alerts

#### Get Recent Alerts

```http
GET /advanced/alerts?limit=10&severity=high
```

**Query Parameters:**
- `limit` (optional, default: 10): Maximum number of alerts (1-100)
- `severity` (optional): Filter by severity (critical, high, medium, low)

**Response:**
```json
{
  "alerts": [
    {
      "id": "alert-456",
      "type": "high_risk",
      "severity": "high",
      "message": "High risk detected for proposal prop-123",
      "timestamp": "2025-12-17T11:00:00Z",
      "proposal_id": "prop-123"
    }
  ]
}
```

### Sentiment

#### Get Sentiment Analysis

```http
GET /advanced/sentiment/{proposalId}
```

**Parameters:**
- `proposalId` (path, required): Unique identifier for the proposal

**Response:**
```json
{
  "proposal_id": "prop-123",
  "overall_sentiment": "positive",
  "sentiment_score": 0.65,
  "analysis": {
    "positive_mentions": 42,
    "negative_mentions": 8,
    "neutral_mentions": 15
  }
}
```

## 🔐 Authentication

Currently, the API is open for public use without authentication. Future versions will implement:

- API key authentication
- OAuth 2.0 support
- Rate limiting per API key

## ⚡ Rate Limiting

Current rate limits:
- **Public**: No strict limits (fair use policy)
- **Future**: 100 requests/minute per IP

Rate limit headers will be included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1702819200
```

## ❌ Error Handling

### Error Response Format

All errors follow this structure:

```json
{
  "error": "NotFound",
  "message": "Proposal with ID prop-123 not found",
  "code": 404,
  "timestamp": "2025-12-17T11:00:00Z"
}
```

### HTTP Status Codes

- `200 OK`: Successful request
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable

## 💡 Examples

### JavaScript/TypeScript

```typescript
const API_BASE = 'https://dao-data-ai.vercel.app/api';

// Get prediction
async function getPrediction(proposalId: string) {
  const response = await fetch(`${API_BASE}/advanced/predictions/${proposalId}`);
  if (!response.ok) throw new Error('Failed to fetch prediction');
  return await response.json();
}

// Batch predictions
async function getBatchPredictions(proposalIds: string[]) {
  const response = await fetch(`${API_BASE}/advanced/predictions/batch`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ proposalIds })
  });
  return await response.json();
}

// Usage
const prediction = await getPrediction('prop-123');
console.log(`Prediction: ${prediction.prediction}`);
```

### Python

```python
import requests

API_BASE = 'https://dao-data-ai.vercel.app/api'

# Get prediction
def get_prediction(proposal_id):
    response = requests.get(f'{API_BASE}/advanced/predictions/{proposal_id}')
    response.raise_for_status()
    return response.json()

# Get governance score
def get_score(proposal_id):
    response = requests.get(f'{API_BASE}/advanced/scores/{proposal_id}')
    response.raise_for_status()
    return response.json()

# Usage
prediction = get_prediction('prop-123')
print(f"Prediction: {prediction['prediction']}")
print(f"Confidence: {prediction['confidence']}")
```

### cURL

```bash
# Get prediction
curl -X GET "https://dao-data-ai.vercel.app/api/advanced/predictions/prop-123" \
  -H "Accept: application/json"

# Batch predictions
curl -X POST "https://dao-data-ai.vercel.app/api/advanced/predictions/batch" \
  -H "Content-Type: application/json" \
  -d '{"proposalIds": ["prop-123", "prop-456"]}'

# Get alerts with filters
curl -X GET "https://dao-data-ai.vercel.app/api/advanced/alerts?limit=5&severity=high" \
  -H "Accept: application/json"
```

## 📝 Data Models

For complete schema definitions, see `openapi.yaml`.

### Key Models

- **Prediction**: ML prediction results with confidence scores
- **Score**: Comprehensive governance scores with component breakdown
- **Alert**: Governance alerts with severity levels
- **Sentiment**: Sentiment analysis with community metrics
- **Error**: Standardized error responses

## 🔗 Resources

- **OpenAPI Specification**: [`openapi.yaml`](./openapi.yaml)
- **Project Repository**: https://github.com/danvolsky-source/dao-data-ai
- **Production App**: https://dao-data-ai.vercel.app
- **Custom Domain**: https://www.sky-mind.com

## 📞 Support

For questions or issues:
- Create an issue on GitHub
- Visit the project homepage
- Check the OpenAPI specification for detailed schemas

## 📄 License

MIT License - See LICENSE file for details

---

**Last Updated**: December 17, 2025  
**API Version**: 1.0.0
