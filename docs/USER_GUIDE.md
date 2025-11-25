# CrisisLens User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Verification Workflow](#verification-workflow)
4. [Managing Items](#managing-items)
5. [Publishing Advisories](#publishing-advisories)
6. [Analytics](#analytics)
7. [Settings](#settings)

## Getting Started

### Logging In

1. Navigate to https://app.crisislen.example.com
2. Click "Sign in with Google" or "Sign in with GitHub"
3. Alternatively, use email/password if registered

### Dashboard Layout

```
┌─────────────────────────────────────────────────┐
│  CrisisLens             🔔  👤 John Doe          │
├─────────────────────────────────────────────────┤
│                                                  │
│  📊 Dashboard  │  📝 Items  │  ⚠️  Advisories   │
│                                                  │
│  ┌──────────────┐  ┌──────────────┐             │
│  │ Pending: 45  │  │ High Risk: 12│             │
│  └──────────────┘  └──────────────┘             │
│                                                  │
│  Recent Items:                                   │
│  ┌─────────────────────────────────────────┐   │
│  │ 🔴 Flood in Mumbai - Risk: 0.85         │   │
│  │ 🟡 Fire reported - Risk: 0.45           │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

## Verification Workflow

### Step 1: Review Incoming Items

1. Go to **Items** → **Pending Review**
2. Items are sorted by risk score (highest first)
3. Click on an item to view details

### Step 2: Examine Claims

Each item contains extracted claims:

```
Claim: "100mm rainfall in Mumbai"
├─ Veracity: 75% (Likely True)
├─ Evidence:
│  ├─ IMD Report: "95mm recorded" (Support: 80%)
│  └─ News Article: "Heavy rains..." (Support: 65%)
└─ Risk Factors:
   ├─ Source Reliability: 90%
   └─ Corroboration: 75%
```

**Actions:**
- ✅ **Verify True**: Claim is accurate
- ❌ **Verify False**: Claim is misinformation
- ⏸️ **Needs Investigation**: More evidence needed
- 📝 **Add Notes**: Provide analyst context

### Step 3: Review Evidence

Evidence is automatically retrieved from:
- Google Fact Check API
- Reverse image search
- Similar past items
- External fact-checkers

**Evaluate Evidence:**
- Check source credibility
- Verify timestamps
- Look for contradictions
- Cross-reference multiple sources

### Step 4: Assess Risk

The system calculates risk score (0-1) based on:

| Factor | Weight | Description |
|--------|--------|-------------|
| Novelty | 20% | How new is this information? |
| Source Reliability | 15% | Is the source trustworthy? |
| Evidence Quality | 20% | How strong is the evidence? |
| Corroboration | 15% | Multiple sources confirm? |
| Sentiment | 10% | Emotional tone |
| Virality | 10% | Spread rate |
| Geographic Clustering | 5% | Locations align? |
| Temporal Consistency | 5% | Timeline makes sense? |

**Risk Levels:**
- 🔴 **High (>0.7)**: Requires immediate attention
- 🟡 **Medium (0.4-0.7)**: Monitor closely
- 🟢 **Low (<0.4)**: Standard processing

### Step 5: Make Decision

High-risk items (>0.7) require human approval:

1. Review all claims and evidence
2. Add analyst notes
3. Click **Approve** or **Reject**
4. Workflow continues automatically

## Managing Items

### Filtering Items

Use filters to find specific items:

```
Status: [All ▼] [Verified ▼] [False ▼]
Risk: [0.0 ——●————— 1.0]
Date: [Last 7 days ▼]
Source: [All ▼] [Twitter] [Reddit] [News]
Topic: [All ▼] [Flood] [Fire] [Violence]
```

### Bulk Actions

Select multiple items:
- **Bulk Verify**: Mark all as true/false
- **Assign to Analyst**: Distribute workload
- **Export**: Download as CSV/JSON
- **Archive**: Move to archived items

### Search

Use advanced search:
```
text:"Mumbai flood" AND risk:>0.7 AND date:>2024-01-01
```

**Search Operators:**
- `text:"query"` - Exact phrase
- `risk:>0.5` - Risk score filter
- `status:pending` - By status
- `source:twitter` - By source
- `date:>2024-01-01` - After date
- `verified:true` - Verification status

## Publishing Advisories

### Advisory Lifecycle

```
Draft → Review → Translate → Publish → Monitor
```

### Creating Advisory

Advisories are auto-drafted for high-risk items:

1. Go to **Advisories** → **Drafts**
2. Select advisory to review
3. Edit sections:
   - **Summary** (2-3 sentences)
   - **What Happened** (detailed narrative)
   - **What's Verified** (confirmed facts)
   - **Recommended Actions** (public guidance)

### Translations

CrisisLens auto-translates to 5 languages:
- 🇮🇳 Hindi (हिंदी)
- 🇮🇳 Marathi (मराठी)
- 🇮🇳 Bengali (বাংলা)
- 🇮🇳 Tamil (தமிழ்)
- 🇮🇳 Telugu (తెలుగు)

Review translations before publish.

### Publishing

1. Click **Publish Advisory**
2. Select distribution channels:
   - ☑️ Web Dashboard
   - ☑️ Mobile App
   - ☑️ Email Alerts
   - ☑️ SMS Notifications
   - ☑️ Webhook
3. Choose severity level
4. Click **Confirm Publish**

### Monitoring Impact

After publishing, track:
- **Views**: How many people saw it
- **Shares**: Social media shares
- **Feedback**: User reports
- **Updates**: Any corrections needed

## Analytics

### Dashboard Metrics

**Overview:**
- Items Processed (24h): 1,234
- Average Risk Score: 0.42
- High-Risk Items: 45
- Active Workflows: 12

**Charts:**
- Risk Score Distribution (histogram)
- Items by Source (pie chart)
- Timeline (line chart)
- Geographic Heatmap

### Reports

Generate custom reports:

1. Go to **Analytics** → **Reports**
2. Select template:
   - Daily Summary
   - Weekly Digest
   - Monthly Overview
   - Custom Query
3. Export as PDF or Excel

### Geospatial Analysis

View crisis events on map:
- **Cluster View**: Group nearby events
- **Heatmap**: Intensity by location
- **Timeline**: Play events chronologically
- **Filters**: By date, type, severity

## Settings

### Profile

- Update name, email
- Change password
- Manage 2FA
- View activity log

### API Keys

Create API keys for programmatic access:

1. Go to **Settings** → **API Keys**
2. Click **Create New Key**
3. Name: "Production Key"
4. Expiration: 90 days
5. Click **Generate**
6. **Copy key immediately** (shown only once!)

### Notifications

Configure alerts:

**Email Notifications:**
- ☑️ High-risk items detected
- ☑️ Items assigned to me
- ☑️ Advisories published
- ☐ Daily digest

**In-App Notifications:**
- ☑️ Real-time alerts
- ☑️ Workflow status changes

### Preferences

- **Theme**: Light / Dark / Auto
- **Language**: English / Hindi / ...
- **Timezone**: IST (UTC+5:30)
- **Items per page**: 20

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `?` | Show shortcuts |
| `/` | Focus search |
| `g d` | Go to dashboard |
| `g i` | Go to items |
| `g a` | Go to advisories |
| `↑ / ↓` | Navigate items |
| `Enter` | Open selected item |
| `v t` | Verify true |
| `v f` | Verify false |
| `Esc` | Close modal |

## Best Practices

### Verification
1. **Always check multiple sources**
2. **Verify timestamps and locations**
3. **Look for original sources, not shares**
4. **Check for image manipulation (EXIF)**
5. **Cross-reference with official channels**

### Speed vs. Accuracy
- High-risk items: Prioritize accuracy
- Low-risk items: Can process faster
- When in doubt: Escalate to supervisor

### Collaboration
- Use **Assign** to distribute work
- Add **Notes** for context
- Tag colleagues with @mention
- Use **Shared Views** for team coordination

## Troubleshooting

### Common Issues

**Q: Item stuck in "Processing"**
A: Workflow may be paused for review. Check workflow status.

**Q: Can't verify claim**
A: Ensure you have "verifier" role. Contact admin.

**Q: Translation missing**
A: Re-trigger translation or contact support.

**Q: High server load**
A: System auto-scales. Wait 2-3 minutes.

### Support

- **Email**: support@crisislen.example.com
- **Slack**: #crisislen-support
- **Phone**: +91-XX-XXXX-XXXX (9 AM - 6 PM IST)
- **Documentation**: docs.crisislen.example.com

## Appendix

### Glossary

- **Claim**: A verifiable statement
- **Evidence**: Supporting or contradicting information
- **Veracity**: Likelihood of truth (0-1)
- **Risk Score**: Composite urgency score (0-1)
- **NLI**: Natural Language Inference
- **Workflow**: Automated verification pipeline

### FAQ

See [FAQ.md](./FAQ.md) for frequently asked questions.
