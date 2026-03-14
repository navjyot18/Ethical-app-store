# ADR 001: Use PostgreSQL for Primary Database

**Status:** Accepted  
**Date:** 2025-02-25  
**Deciders:** Navjyot Bhele

## Context
We need to choose a database for storing app metadata, analysis results, 
scores, and historical data. Requirements:
- Store structured data (apps, scores)
- Store semi-structured data (trackers, policy findings)
- Support fast search and filtering
- Handle relationships (apps → multiple analyses)
- Scale to 10,000 apps, 100,000 analyses

Options considered:
1. PostgreSQL (SQL + JSONB)
2. MongoDB (NoSQL)
3. SQLite (Embedded SQL)

## Decision
We will use **PostgreSQL 15** as our primary database.

## Rationale

### Why PostgreSQL over MongoDB:
- **Structured queries:** Users search by score, category, date
  - PostgreSQL: Native indexes, fast
  - MongoDB: Slower for complex multi-field queries
  
- **Data relationships:** Apps have multiple historical analyses
  - PostgreSQL: Foreign keys, JOIN support
  - MongoDB: Manual reference management
  
- **Data integrity:** Scores must be 0-100, no duplicate package names
  - PostgreSQL: CHECK constraints, UNIQUE constraints
  - MongoDB: Validation in application code only
  
- **Flexibility:** Trackers/policy findings vary in structure
  - PostgreSQL: JSONB columns (best of both worlds)
  - MongoDB: Native JSON support (but slower queries)

    1. Your Data is Actually Structured
    Every app has:

    ✅ Package name
    ✅ App name
    ✅ Developer
    ✅ Score (privacy, transparency, etc.)
    ✅ Category
    ✅ Analyzed date

    This is perfect for SQL tables (rows and columns).

    2. You Need to Search and Filter
    Users will search:

    "Show me all Social Media apps"
    "Show me apps with score > 70"
    "Show me apps analyzed in the last 7 days"
    "Show me all apps by Meta"

### Why PostgreSQL over SQLite:
- SQLite is file-based, not suitable for web applications
- No concurrent write support
- Limited to single server

### Why PostgreSQL 15 Specifically:
- JSONB performance improvements in v15
- Better full-text search (tsvector)
- Widely supported by hosting providers (Railway, Render, Vercel)

## Consequences

### Positive:
✅ Fast queries for filtering/sorting
✅ Data integrity enforced at DB level
✅ Easy to add indexes for performance
✅ Full-text search built-in
✅ JSONB for flexible fields
✅ Free hosting options available

### Negative:
⚠️ Requires learning SQL (but you likely already know it)
⚠️ Schema migrations needed when structure changes
⚠️ Harder to scale horizontally than NoSQL (but won't be an issue until millions of records)

### Neutral:
- Need to run PostgreSQL server (Docker makes this easy)
- JSONB queries are less intuitive than native JSON in MongoDB

## Alternatives Considered

### MongoDB
- ❌ Slower for multi-field queries (category + score + date)
- ❌ No built-in data validation
- ✅ Easier to change schema
- Verdict: Flexibility not worth the query performance hit

### SQLite
- ❌ Not suitable for production web apps
- ✅ Zero configuration
- Verdict: Good for prototyping, not for deployment

## References
- [PostgreSQL vs MongoDB Benchmark](https://www.postgresql.org/about/news/...)
- [JSONB Performance](https://www.postgresql.org/docs/15/datatype-json.html)
- [Why Uber switched from PostgreSQL to MySQL (and why we're not)](https://eng.uber.com/postgres-to-mysql-migration/)

## Status
**Accepted** - Implemented in v1.0.0

Visual Example - Complete Data
Apps Table:

┌────┬─────────────────────────┬────────────┬──────────┬──────────────┐
│ id │ package_name            │ app_name   │ developer│ category     │
├────┼─────────────────────────┼────────────┼──────────┼──────────────┤
│ 1  │ com.instagram.android   │ Instagram  │ Meta     │ Social Media │
│ 2  │ org.thoughtcrime...     │ Signal     │ Signal F.│ Messaging    │
│ 3  │ com.whatsapp            │ WhatsApp   │ Meta     │ Messaging    │
└────┴─────────────────────────┴────────────┴──────────┴──────────────┘
Analysis_Results Table:
┌────┬────────┬─────────────┬───────────┬─────────────┬─────────────────────┐
│ id │ app_id │ analyzed_at │ overall   │ privacy     │ trackers            │
│    │        │             │ _score    │ _score      │                     │
├────┼────────┼─────────────┼───────────┼─────────────┼─────────────────────┤
│ 1  │ 1      │ 2025-02-25  │ 32        │ 25          │ [Firebase, FB SDK]  │
│ 2  │ 1      │ 2025-01-15  │ 35        │ 28          │ [Firebase, FB SDK]  │
│ 3  │ 2      │ 2025-02-25  │ 92        │ 95          │ []                  │
│ 4  │ 3      │ 2025-02-25  │ 48        │ 45          │ [Google Analytics]  │
└────┴────────┴─────────────┴───────────┴─────────────┴─────────────────────┘



# Database Design

## Overview

We use **PostgreSQL 15** to store app metadata and analysis results.

See [ADR 001](decisions/001-use-postgresql.md) for why we chose PostgreSQL.

---

## Tables

We have **2 main tables**:

1. **`apps`** - Basic app information
2. **`analysis_results`** - Analysis scores and findings

---

## Table 1: `apps`

Stores basic information about each app (like a contact list).

### Schema
```sql
CREATE TABLE apps (
    id SERIAL PRIMARY KEY,                    -- Unique ID (auto-increments: 1, 2, 3...)
    package_name VARCHAR(255) UNIQUE NOT NULL, -- e.g., "com.instagram.android"
    app_name VARCHAR(255) NOT NULL,           -- e.g., "Instagram"
    developer VARCHAR(255),                   -- e.g., "Meta Platforms, Inc."
    category VARCHAR(100),                    -- e.g., "Social Media"
    platform VARCHAR(20),                     -- "android", "ios", or "both"
    icon_url TEXT,                            -- URL to app icon
    privacy_policy_url TEXT,                  -- URL to privacy policy
    description TEXT,                         -- App description
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Example Data

| id | package_name | app_name | developer | category | platform |
|----|--------------|----------|-----------|----------|----------|
| 1 | com.instagram.android | Instagram | Meta Platforms, Inc. | Social Media | android |
| 2 | org.thoughtcrime.securesms | Signal | Signal Foundation | Messaging | android |
| 3 | com.whatsapp | WhatsApp | Meta Platforms, Inc. | Messaging | android |

### Constraints

- `package_name` must be unique (no duplicate apps)
- `app_name` and `package_name` are required (NOT NULL)
- `platform` must be one of: 'android', 'ios', 'both'

---

## Table 2: `analysis_results`

Stores the results of each analysis (like a report card). An app can have multiple analyses over time.

### Schema
```sql
CREATE TABLE analysis_results (
    id SERIAL PRIMARY KEY,
    app_id INTEGER REFERENCES apps(id) ON DELETE CASCADE,  -- Links to apps table
    app_version VARCHAR(50),                               -- e.g., "305.0.0.0.71"
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Scores (all 0-100)
    overall_score INTEGER CHECK (overall_score BETWEEN 0 AND 100),
    privacy_score INTEGER CHECK (privacy_score BETWEEN 0 AND 100),
    transparency_score INTEGER CHECK (transparency_score BETWEEN 0 AND 100),
    resource_score INTEGER CHECK (resource_score BETWEEN 0 AND 100),
    design_score INTEGER CHECK (design_score BETWEEN 0 AND 100),
    
    -- Raw data (stored as JSONB for flexibility)
    trackers JSONB,           -- List of trackers: [{"name": "...", "category": "..."}, ...]
    permissions JSONB,        -- List of permissions: ["CAMERA", "LOCATION", ...]
    policy_analysis JSONB,    -- Policy findings: {"sells_data": true, ...}
    review_summary JSONB,     -- Review analysis: {"battery_mentions": 45, ...}
    
    -- Metadata
    scoring_version VARCHAR(20) DEFAULT 'v1.0.0',
    analysis_duration_seconds INTEGER
);
```

### Example Data

| id | app_id | analyzed_at | overall_score | privacy_score | trackers |
|----|--------|-------------|---------------|---------------|----------|
| 1 | 1 | 2025-02-25 14:00 | 32 | 25 | `[{"name": "Firebase"}, ...]` |
| 2 | 1 | 2025-01-15 10:30 | 35 | 28 | `[{"name": "Firebase"}, ...]` |
| 3 | 2 | 2025-02-25 14:15 | 92 | 95 | `[]` |

### Relationship
```
apps (id=1, name="Instagram")
  ↓
  ├─ analysis_results (id=1, app_id=1, date=Feb 25, score=32)
  └─ analysis_results (id=2, app_id=1, date=Jan 15, score=35)
```

**Translation:** Instagram (app_id=1) has been analyzed twice.

---

## Why JSONB for Trackers/Permissions/Policy?

### The Problem

Different apps have different data:
- Instagram: 12 trackers
- Signal: 0 trackers
- WhatsApp: 4 trackers

**Traditional approach (separate tables):**
```
analysis_results
  └── trackers table
        ├── tracker 1
        ├── tracker 2
        └── tracker 3
```

**Problem:** Requires multiple queries, complex JOINs.

### Our Solution: JSONB

Store lists directly in the `analysis_results` table:
```json
{
  "trackers": [
    {"name": "Google Firebase Analytics", "category": "Analytics"},
    {"name": "Facebook SDK", "category": "Advertising"}
  ]
}
```

**Benefits:**
- ✅ Flexible (can store 0 to 100 trackers)
- ✅ One query to get all data
- ✅ Can still search inside JSON: `WHERE trackers @> '{"name": "Firebase"}'`

**Tradeoff:**
- ⚠️ Less "normalized" (not pure SQL best practice)
- ✅ But much simpler for our use case

---

## Indexes (For Speed)

We add indexes to make searches fast:
```sql
-- Find apps by package name quickly
CREATE INDEX idx_apps_package_name ON apps(package_name);

-- Find apps by category quickly
CREATE INDEX idx_apps_category ON apps(category);

-- Find analyses by app quickly
CREATE INDEX idx_analysis_app_id ON analysis_results(app_id);

-- Find recent analyses quickly
CREATE INDEX idx_analysis_date ON analysis_results(analyzed_at DESC);

-- Find apps by score quickly
CREATE INDEX idx_analysis_overall_score ON analysis_results(overall_score);
```

**What indexes do:** Like an index in a book - helps find things faster.

Without index: Search 1,000 apps one by one (slow)  
With index: Jump directly to apps in "Social Media" category (fast)

---

## Common Queries

### Get an app with its latest score
```sql
SELECT 
    a.app_name,
    a.developer,
    ar.overall_score,
    ar.privacy_score,
    ar.analyzed_at
FROM apps a
JOIN analysis_results ar ON a.id = ar.app_id
WHERE a.package_name = 'com.instagram.android'
ORDER BY ar.analyzed_at DESC
LIMIT 1;
```

**Result:**
```
app_name: Instagram
developer: Meta Platforms, Inc.
overall_score: 32
privacy_score: 25
analyzed_at: 2025-02-25 14:00:00
```

### Find all high-scoring social media apps
```sql
SELECT 
    a.app_name,
    ar.overall_score
FROM apps a
JOIN analysis_results ar ON a.id = ar.app_id
WHERE a.category = 'Social Media'
  AND ar.overall_score > 70
  AND ar.id IN (
      -- Get only the latest analysis for each app
      SELECT MAX(id) FROM analysis_results GROUP BY app_id
  )
ORDER BY ar.overall_score DESC;
```

### Get score history for an app
```sql
SELECT 
    analyzed_at,
    overall_score,
    privacy_score
FROM analysis_results
WHERE app_id = (SELECT id FROM apps WHERE package_name = 'com.instagram.android')
ORDER BY analyzed_at DESC;
```

**Result:**
```
analyzed_at          overall_score  privacy_score
2025-02-25 14:00     32             25
2025-01-15 10:30     35             28
2024-12-10 09:00     33             26
```

---

## Data Migration

When we need to change the database structure, we use migrations.

Example: Adding a new column
```sql
-- Migration: Add 'downloads' column to apps table

ALTER TABLE apps 
ADD COLUMN downloads BIGINT DEFAULT 0;
```

**Best practice:** Use a migration tool like Alembic (Python) to track changes.

---

## Backup Strategy

### Development
- Use Docker volumes (data persists even if container is deleted)

### Production
- Automated daily backups via hosting provider (Railway/Render)
- Keep last 7 days of backups
- Export important data weekly to S3

---

## Future Considerations

As we scale, we might:

1. **Add caching layer** (Redis)
   - Cache popular app scores
   - Reduce database load

2. **Partition analysis_results by date**
   - Old analyses (>1 year) moved to separate table
   - Keeps main table fast

3. **Read replicas**
   - Primary database for writes
   - Replica databases for reads
   - Handle more traffic

4. **Separate trackers table**
   - If we need to analyze tracker trends across all apps
   - Not needed for MVP

---

## Testing

Sample data for testing:
```sql
-- Insert test apps
INSERT INTO apps (package_name, app_name, developer, category, platform)
VALUES 
    ('com.test.app1', 'Test App 1', 'Test Dev', 'Social Media', 'android'),
    ('com.test.app2', 'Test App 2', 'Test Dev', 'Productivity', 'android');

-- Insert test analyses
INSERT INTO analysis_results (
    app_id, 
    overall_score, 
    privacy_score, 
    transparency_score, 
    resource_score, 
    design_score,
    trackers,
    permissions
)
VALUES 
    (1, 50, 45, 55, 50, 50, '[]'::jsonb, '["INTERNET"]'::jsonb),
    (2, 80, 85, 75, 80, 80, '[]'::jsonb, '["INTERNET"]'::jsonb);
```

---

## References

- PostgreSQL JSONB documentation: https://www.postgresql.org/docs/15/datatype-json.html
- Indexing best practices: https://www.postgresql.org/docs/15/indexes.html