# Database Operations

I need to perform database operations on the Fizz production PostgreSQL database.

## Connect to Database

```powershell
Import-Module .\FizzAws.psm1

# Open psql shell
Enter-FizzContainer -Container postgres -Shell "/bin/bash"
# Then run: psql -U fizz -d fizz

# Or run a quick query
Invoke-FizzDocker -Container postgres -Command "psql -U fizz -d fizz -c 'SELECT COUNT(*) FROM leads'"
```

## Common Queries

```sql
-- Count leads by status
SELECT status, COUNT(*) FROM leads GROUP BY status;

-- Recent leads
SELECT id, domain, status, created_at FROM leads ORDER BY created_at DESC LIMIT 20;

-- Check campaigns
SELECT id, name, status, created_at FROM campaigns ORDER BY created_at DESC LIMIT 10;

-- Database size
SELECT pg_size_pretty(pg_database_size('fizz'));
```

## Prisma Operations

```powershell
# Open Prisma Studio (web UI)
Invoke-FizzDocker -Container app -Command "npx prisma studio"

# Run migrations
Invoke-FizzDocker -Container app -Command "npx prisma migrate deploy"

# Generate client
Invoke-FizzDocker -Container app -Command "npx prisma generate"
```

## What I Need to Do
[Describe the database operation - query data, check stats, run migration, etc.]
