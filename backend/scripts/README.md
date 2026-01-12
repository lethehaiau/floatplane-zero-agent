# Backend Scripts

This directory contains utility scripts for development, testing, and maintenance.

## Testing Scripts

### `test_search_interactive.py`
Interactive CLI for testing search functionality.

**Usage:**
```bash
# From backend directory
python scripts/test_search_interactive.py

# Or inside Docker
docker exec -it floatplane-backend python scripts/test_search_interactive.py
```

**Features:**
- Enter multiple search queries interactively
- See results from Tavily (AI summary) or DuckDuckGo fallback
- Type 'exit' or 'quit' to stop

### `test_search_once.py`
One-shot search test for quick verification.

**Usage:**
```bash
# Test a single query
python scripts/test_search_once.py "weather in HCMC today"

# Inside Docker
docker exec floatplane-backend python scripts/test_search_once.py "your query here"
```

**Features:**
- Quick test without interactive prompts
- Good for CI/CD or automated testing
- Shows which search provider was used (Tavily vs DuckDuckGo)

## Adding New Scripts

When creating new scripts in this directory:

1. **Add path configuration** at the top:
   ```python
   import sys
   from pathlib import Path

   # Add parent directory to path so we can import from app/
   backend_dir = Path(__file__).parent.parent
   sys.path.insert(0, str(backend_dir))

   from app.tools.search import search_internet
   ```

2. **Use clear naming**: `test_*.py` for testing, `migrate_*.py` for migrations, etc.

3. **Add docstrings** with usage examples

4. **Update this README** with script description and usage

## Common Script Types

Recommended structure for this folder:

- `test_*.py` - Manual testing and verification scripts
- `migrate_*.py` - Database migration utilities
- `seed_*.py` - Database seeding scripts
- `export_*.py` - Data export utilities
- `cleanup_*.py` - Maintenance and cleanup tasks
