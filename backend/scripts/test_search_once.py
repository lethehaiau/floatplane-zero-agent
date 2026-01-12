"""
Simple one-shot search test script.

Run: python scripts/test_search_once.py "your query here"
"""
import sys
import traceback
from pathlib import Path

# Add parent directory to path so we can import from app/
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.tools.search import search_internet


def main():
    """Test search with command line query."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_search_once.py \"your search query\"")
        print("Example: python scripts/test_search_once.py \"weather in HCMC today\"")
        sys.exit(1)

    query = " ".join(sys.argv[1:])

    print("="*80)
    print(f"Testing search with query: '{query}'")
    print("="*80)

    try:
        results = search_internet(query, max_results=5)

        if not results:
            print("❌ No results found or search failed")
            sys.exit(1)

        print(f"\n✅ Found {len(results)} results:\n")

        for i, result in enumerate(results, 1):
            print(f"[{i}] {result['title']}")
            print(f"    {result['snippet'][:200]}{'...' if len(result['snippet']) > 200 else ''}")
            if result['link']:
                print(f"    Link: {result['link']}")
            print()

        print("="*80)
        print("✅ Search test completed successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
