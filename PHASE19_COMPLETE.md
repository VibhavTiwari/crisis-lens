# Phase 19: Advanced NLP & Analytics - Complete!

## Components Implemented

### 1. Coreference Resolution (`ml/nlp/coreference.py`)
**Pronoun resolution and entity mention clustering:**
- Simplified coreference using spaCy dependency parsing
- Pronoun-antecedent matching
- Entity mention extraction
- Mention clustering by text similarity

**Methods:**
- `resolve_simplified()` - Resolve pronouns to antecedents
- `extract_entity_mentions()` - Extract all entity mentions
- `cluster_mentions()` - Group mentions of same entity

**Note:** Uses simplified approach. Production would use:
- AllenNLP Coreference Resolution
- Stanford CoreNLP
- Hugging Face coreference models

### 2. Temporal Reasoning (`ml/nlp/temporal_reasoning.py`)
**Timeline extraction and temporal analysis:**
- Absolute date extraction (YYYY-MM-DD, DD/MM/YYYY)
- Relative time expressions (yesterday, last week, tomorrow)
- Time of day extraction (HH:MM AM/PM)
- Timeline construction from multiple documents
- Temporal relation detection (before, after, during)

**Methods:**
- `extract_temporal_expressions()` - Extract dates/times
- `build_timeline()` - Build chronological timeline
- `find_temporal_relations()` - Extract temporal connectives
- `normalize_to_absolute()` - Convert relative to absolute dates
- `compute_duration()` - Calculate time spans

**Features:**
- Reference date support
- Automatic sorting by datetime
- Duration calculations
- Temporal relation types (BEFORE, AFTER, DURING, SINCE, UNTIL, WHEN)

### 3. Geospatial Analysis (`ml/nlp/geospatial.py`)
**Location extraction and spatial reasoning:**
- Location entity extraction (GPE, LOC, FAC)
- Geocoding with Nominatim (OpenStreetMap)
- Distance calculations (geodesic)
- Proximity search (radius-based)
- Location clustering (by distance)
- Spatial distribution analysis

**Methods:**
- `extract_locations()` - Extract location mentions
- `geocode_location()` - Convert name to coordinates
- `calculate_distance()` - Distance between two points
- `find_nearby_locations()` - Radius search
- `cluster_locations()` - Group nearby locations
- `analyze_spatial_distribution()` - Center, spread, bounding box

**Use Cases:**
- Find all locations mentioned in text
- Calculate distance between crisis points
- Cluster related incidents geographically
- Compute crisis epicenter

### 4. Social Network Analysis (`ml/nlp/social_network.py`)
**Information spread and influence analysis:**
- Network construction from interactions
- Influencer detection (PageRank)
- Community detection (Louvain algorithm)
- Centrality measures (degree, betweenness, closeness, eigenvector)
- Information propagation analysis
- Shortest path finding

**Methods:**
- `build_network()` - Create directed graph
- `find_influencers()` - Top influencers by PageRank
- `detect_communities()` - Community clustering
- `calculate_centrality_measures()` - 4 centrality metrics
- `analyze_information_spread()` - BFS propagation analysis
- `export_for_visualization()` - Format for vis tools

**Metrics:**
- **Degree centrality** - Number of connections
- **Betweenness** - Bridge between groups
- **Closeness** - Average distance to others
- **Eigenvector** - Connected to important nodes
- **PageRank** - Influence score

### 5. Sentiment Analysis (`ml/nlp/sentiment.py`)
**Crisis sentiment and urgency detection:**
- VADER sentiment analysis (social media optimized)
- Positive/negative/neutral classification
- Urgency marker detection
- Emotion distribution analysis
- Crisis-specific sentiment

**Methods:**
- `analyze()` - Basic sentiment (compound, pos, neg, neu)
- `analyze_batch()` - Multiple texts
- `get_emotion_distribution()` - Sentiment counts
- `detect_urgency_markers()` - Urgency keywords + exclamations
- `analyze_crisis_sentiment()` - Combined sentiment + urgency

**Urgency Keywords:**
- urgent, emergency, critical, immediate, ASAP
- help, danger, warning, alert, breaking

**Alarm Keywords:**
- fire, explosion, attack, disaster, crisis
- emergency, evacuate, danger

**Urgency Score:** 0-1 (weighted combination)

## Dependencies Added

```toml
# Advanced NLP & Analytics
spacy-transformers = "^1.3.0"
neuralcoref = {git = "https://github.com/huggingface/neuralcoref.git"}
sutime = "^1.0.0"
geopandas = "^0.14.0"
networkx = "^3.2"
pyvis = "^0.3.2"
geopy = "^2.4.0"
vaderSentiment = "^3.3.2"
```

## Usage Examples

### Coreference Resolution
```python
from ml.nlp.coreference import coreference_resolver

text = "John went to the store. He bought milk."
result = coreference_resolver.resolve_simplified(text)

print(result['chains'])  # [{'pronoun': 'He', 'antecedent': 'John'}]
```

### Temporal Reasoning
```python
from ml.nlp.temporal_reasoning import temporal_reasoner
from datetime import datetime

text = "The explosion happened yesterday at 3:00 PM"
expressions = temporal_reasoner.extract_temporal_expressions(
    text,
    reference_date=datetime.now()
)

# Build timeline
texts = ["Event A happened yesterday", "Event B occurred today"]
timeline = temporal_reasoner.build_timeline(texts)
```

### Geospatial Analysis
```python
from ml.nlp.geospatial import geospatial_analyzer

# Extract locations
text = "Flooding reported in Mumbai and Delhi"
locations = geospatial_analyzer.extract_locations(text)

# Geocode
coords = geospatial_analyzer.geocode_location("Mumbai")
print(f"Coordinates: {coords['latitude']}, {coords['longitude']}")

# Calculate distance
dist = geospatial_analyzer.calculate_distance(
    (19.0760, 72.8777),  # Mumbai
    (28.7041, 77.1025)   # Delhi
)
print(f"Distance: {dist['km']} km")

# Cluster nearby locations
clusters = geospatial_analyzer.cluster_locations(locations, max_distance_km=50)
```

### Social Network Analysis
```python
from ml.nlp.social_network import social_network_analyzer

# Build network
interactions = [
    {'source': 'UserA', 'target': 'UserB', 'type': 'retweet', 'weight': 1.0},
    {'source': 'UserB', 'target': 'UserC', 'type': 'reply', 'weight': 0.5},
]
graph = social_network_analyzer.build_network(interactions)

# Find influencers
influencers = social_network_analyzer.find_influencers(top_n=10)

# Detect communities
communities = social_network_analyzer.detect_communities()

# Analyze spread
spread = social_network_analyzer.analyze_information_spread('UserA', max_hops=3)
print(f"Total reach: {spread['total_reach']} users")
```

### Sentiment Analysis
```python
from ml.nlp.sentiment import sentiment_analyzer

text = "URGENT! Fire in building! Evacuate immediately!"

# Basic sentiment
sentiment = sentiment_analyzer.analyze(text)
print(f"Sentiment: {sentiment['sentiment']}, Compound: {sentiment['compound']}")

# Crisis sentiment
crisis_analysis = sentiment_analyzer.analyze_crisis_sentiment(text)
print(f"Urgency score: {crisis_analysis['urgency']['urgency_score']}")
print(f"Requires attention: {crisis_analysis['requires_attention']}")
```

## Integration Example

```python
# Comprehensive text analysis
from ml.nlp.coreference import coreference_resolver
from ml.nlp.temporal_reasoning import temporal_reasoner
from ml.nlp.geospatial import geospatial_analyzer
from ml.nlp.sentiment import sentiment_analyzer

def analyze_crisis_text(text: str):
    """Comprehensive NLP analysis"""
    
    # 1. Resolve coreferences
    coreference = coreference_resolver.resolve_simplified(text)
    
    # 2. Extract temporal info
    timeline = temporal_reasoner.extract_temporal_expressions(text)
    
    # 3. Extract locations
    locations = geospatial_analyzer.extract_locations(text)
    
    # 4. Sentiment and urgency
    sentiment = sentiment_analyzer.analyze_crisis_sentiment(text)
    
    return {
        'coreference_chains': coreference['chains'],
        'temporal_expressions': timeline,
        'locations': locations,
        'sentiment': sentiment,
        'requires_urgent_attention': (
            sentiment['requires_attention'] and
            sentiment['urgency']['urgency_score'] > 0.7
        )
    }
```

## Next Steps (Phase 20 - Final)

Create comprehensive documentation and deployment guide:
- API documentation (OpenAPI/Swagger)
- User guides
- Architecture diagrams
- Deployment playbook
- Security guidelines
- Performance tuning guide
