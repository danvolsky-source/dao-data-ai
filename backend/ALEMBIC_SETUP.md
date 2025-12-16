# Alembic Database Migrations Setup

This guide explains how to set up and use Alembic for database migrations in the DAO Data AI project.

## Prerequisites

- Python 3.10+
- PostgreSQL database
- All dependencies from `requirements.txt` installed

## Initial Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the `backend` directory with your database credentials:

```env
DB_USER=your_db_user
DB_PASS=your_db_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dao_data_ai
```

### 3. Initialize Alembic (Already Done)

The Alembic structure has been set up with:
- `alembic.ini` - Configuration file
- `alembic/` directory will contain migration scripts
- `alembic/env.py` - Environment configuration
- `alembic/versions/` - Migration version files

### 4. Create Database Models

Create your SQLAlchemy models in `backend/models.py`. Example:

```python
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Proposal(Base):
    __tablename__ = "proposals"
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    status = Column(String, nullable=False)
    votes_for = Column(Integer, default=0)
    votes_against = Column(Integer, default=0)
    prediction = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Vote(Base):
    __tablename__ = "votes"
    
    id = Column(String, primary_key=True)
    proposal_id = Column(String, nullable=False)
    voter = Column(String, nullable=False)
    choice = Column(String, nullable=False)
    voting_power = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Delegate(Base):
    __tablename__ = "delegates"
    
    id = Column(String, primary_key=True)
    address = Column(String, unique=True, nullable=False)
    delegated_votes = Column(Integer, default=0)
    votes_count = Column(Integer, default=0)
    proposals_created = Column(Integer, default=0)
    participation_rate = Column(Float, default=0.0)
    joined_at = Column(DateTime, default=datetime.utcnow)
```

## Using Alembic

### Create a New Migration

After modifying your models, generate a new migration:

```bash
cd backend
alembic revision --autogenerate -m "Add proposals, votes, and delegates tables"
```

### Apply Migrations

Apply all pending migrations to the database:

```bash
alembic upgrade head
```

### Rollback Migrations

Rollback the last migration:

```bash
alembic downgrade -1
```

Rollback to a specific revision:

```bash
alembic downgrade <revision_id>
```

### View Migration History

See current database version:

```bash
alembic current
```

View migration history:

```bash
alembic history
```

## Common Commands

```bash
# Create a new migration
alembic revision -m "description"

# Auto-generate migration from model changes
alembic revision --autogenerate -m "description"

# Upgrade to latest
alembic upgrade head

# Upgrade by one version
alembic upgrade +1

# Downgrade by one version
alembic downgrade -1

# Downgrade to specific version
alembic downgrade <revision>

# Show current version
alembic current

# Show history
alembic history --verbose
```

## Best Practices

1. **Always review auto-generated migrations** before applying them
2. **Test migrations** in development environment first
3. **Create backups** before running migrations in production
4. **Use descriptive names** for migration files
5. **Never modify** existing migration files after they've been applied
6. **Keep migrations small** and focused on single changes
7. **Document complex migrations** with comments in the migration file

## Troubleshooting

### Database Connection Issues

If you get connection errors, verify:
- Database credentials in `.env` are correct
- PostgreSQL service is running
- Database exists and is accessible

### Migration Conflicts

If migrations are out of sync:
```bash
# Check current state
alembic current

# Check history
alembic history

# Stamp to specific version (use with caution)
alembic stamp <revision>
```

### Reset All Migrations (Development Only)

⚠️ **Warning: This will delete all data!**

```bash
# Drop all tables
psql -U your_db_user -d dao_data_ai -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Re-run migrations
alembic upgrade head
```

## Additional Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
