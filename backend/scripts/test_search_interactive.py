"""
Interactive search testing script.

Run: python test_search_interactive.py
"""
from app.tools.search import search_internet


def main():
    """Interactive search testing."""
    print("="*80)
    print("INTERACTIVE SEARCH TEST")
    print("="*80)
    print("Enter your search queries. Type 'exit' or 'quit' to stop.\n")

    while True:
        # Get query from user
        query = input("\nEnter search query: ").strip()

        # Exit condition
        if query.lower() in ['exit', 'quit', '']:
            print("\nExiting...")
            break

        # Perform search
        print(f"\nSearching for: '{query}'...")
        print("-"*80)

        try:
            results = search_internet(query, max_results=5)

            if not results:
                print("❌ No results found or search failed")
                continue

            print(f"✅ Found {len(results)} results:\n")

            for i, result in enumerate(results, 1):
                print(f"[{i}] {result['title']}")
                print(f"    {result['snippet']}")
                print(f"    Link: {result['link']}")
                print()

        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
