# Database Schema Explanation

## Overview

This document explains what the `schema.sql` file does in the project.

The schema file defines the **structure of the PostgreSQL database** used by the application.

---

## 1. Create Folder Structure

**Command:**

```bash
mkdir -p src/models
```

**What it does:**

Creates the folder:

```
src/
 └── models/
```

The `-p` flag ensures parent folders are created if they don't exist.

---

## 2. Create Schema File

**Command:**

```bash
cat > src/models/schema.sql << 'EOF'
```

This creates a file called `src/models/schema.sql`. Everything written until `EOF` will be saved in this file.

---

## 3. Enable UUID Extension

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

This enables UUID generation in PostgreSQL.

**Example UUID:**

```
550e8400-e29b-41d4-a716-446655440000
```

---

## 4. Apps Table

```sql
CREATE TABLE apps (...)
```

This table stores basic information about apps.

**Example row:**

| id | app_name  | developer | category  |
|----|-----------|-----------|-----------|
| 1  | WhatsApp  | Meta      | Messaging |

---

## 5. Analysis Results Table

```sql
CREATE TABLE analysis_results (...)
```

This table stores analysis scores for each app.

**Example:**

| app_id | privacy_score | overall_score |
|--------|---------------|---------------|
| 1      | 70            | 75            |

The `app_id` connects the analysis to the app in the `apps` table.

---

## 6. Indexes (Performance Optimization)

**Example:**

```sql
CREATE INDEX idx_apps_package_name ON apps(package_name);
```

Indexes help the database search data faster.

| Without Index       | With Index                  |
|---------------------|-----------------------------|
| Scan entire table   | Jump directly to the data   |

---

## 7. Full Text Search

```sql
ALTER TABLE apps ADD COLUMN search_vector tsvector;
```

This enables text searching inside the database.

**Example search:**

```
"messaging meta"
```

instead of exact match searches.

---

## 8. Database Triggers

Triggers automatically run functions when data changes.

**Example:**

```sql
CREATE TRIGGER apps_search_update
BEFORE INSERT OR UPDATE ON apps
FOR EACH ROW EXECUTE FUNCTION update_search_vector();
```

This automatically updates the search field when an app is added or updated.

---

## 9. Auto Update Timestamp

```sql
CREATE TRIGGER apps_updated_at
BEFORE UPDATE ON apps
FOR EACH ROW EXECUTE FUNCTION update_updated_at();
```

This automatically updates the `updated_at` column whenever a record is updated.

---

## 10. Run Schema Inside Docker Database

**Command:**

```bash
docker exec -i app_analyzer_db psql -U analyzer -d app_analyzer < src/models/schema.sql
```

**Explanation:**

| Part                  | Meaning                          |
|-----------------------|----------------------------------|
| `docker exec`         | Run command inside container     |
| `app_analyzer_db`     | Docker container name            |
| `psql`                | PostgreSQL command line tool     |
| `-U analyzer`         | Database user                    |
| `-d app_analyzer`     | Database name                    |
| `< schema.sql`        | Run SQL commands from file       |

---

## Final Database Structure

**Database:** `app_analyzer`

**Tables created:**
- `apps`
- `analysis_results`

**Features enabled:**
- Indexes for fast search
- Full text search
- Automatic timestamps
- Automatic search updates

---

## Summary

This schema file sets up the entire database structure for the application.

It creates **tables**, **indexes**, **triggers**, and **functions** so the backend can store and analyze app data efficiently.