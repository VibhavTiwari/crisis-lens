# Phase 21: Real-time Features & Streaming Setup

## Quick Start

1. **Start Infrastructure**
```bash
docker-compose up -d
```

2. **Initialize Kafka Topics**
```bash
python infrastructure/kafka/init_topics.py
```

3. **Start API Server**
```bash
python apps/api/main_realtime.py
```

4. **Start Kafka Consumers** (in separate terminal)
```bash
python scripts/run_consumers.py
```

5. **Start Frontend** (in separate terminal)
```bash
cd apps/web
npm run dev
```

6. **Access Services**
- Frontend: http://localhost:3000
- API: http://localhost:8000
- Kafka UI: http://localhost:8080
- API Docs: http://localhost:8000/docs

## Verify Installation

```bash
python verify_phase21.py
```

## Test WebSocket Connection

```javascript
// In browser console at localhost:3000
const ws = new WebSocket('ws://localhost:8000/ws?token=YOUR_TOKEN')
ws.onmessage = (event) => console.log('Received:', JSON.parse(event.data))
ws.send(JSON.stringify({ type: 'ping' }))
```

## Test SSE Connection

```javascript
// In browser console
const sse = new EventSource('http://localhost:8000/api/sse/stream?token=YOUR_TOKEN')
sse.onmessage = (event) => console.log('SSE:', JSON.parse(event.data))
```

## Publish Test Events

```python
# In Python shell
from services.kafka_producer import publish_raw_item, publish_alert

# Publish test item
await publish_raw_item({
    'id': 'test-001',
    'title': 'Test Crisis Event',
    'content': 'This is a test',
    'risk_score': 0.85
})

# Publish test alert
await publish_alert({
    'severity': 'high',
    'message': 'Test alert',
    'type': 'test'
})
```

## Monitor Kafka

Access Kafka UI at http://localhost:8080 to:
- View topics and partitions
- Monitor consumer lag
- Inspect messages
- View consumer groups

## Troubleshooting

### Kafka Connection Issues
```bash
# Check Kafka is running
docker ps | grep kafka

# View Kafka logs
docker logs crisis-kafka

# Restart services
docker-compose restart kafka zookeeper
```

### WebSocket Not Connecting
- Ensure API server is running
- Check authentication token is valid
- Verify CORS settings in main_realtime.py

### No Real-time Updates
- Check Kafka consumers are running
- Verify topics exist: `python infrastructure/kafka/init_topics.py`
- Monitor consumer logs for errors

## Production Considerations

1. **Kafka**: Use managed Kafka (Confluent Cloud, AWS MSK)
2. **WebSocket**: Use Redis for connection state in multi-instance setup
3. **Notifications**: Configure external services (SendGrid, Twilio, FCM)
4. **Monitoring**: Add Prometheus metrics
5. **Scaling**: Run multiple consumer instances for each group
