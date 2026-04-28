from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults


@tool
def search_delivery_track_record(supplier_name: str) -> str:
    """
    Search for a supplier's delivery performance and logistics track record.
    Looks for on-time delivery rates, shipping delays, lead time issues,
    logistics partnerships, and order fulfilment reliability.
    Input: the supplier company name.
    Returns: delivery performance findings from web sources.
    """
    searcher = TavilySearchResults(max_results=4)
    queries = [
        f"{supplier_name} delivery on-time performance shipping delay",
        f"{supplier_name} lead time logistics order fulfilment",
    ]
    all_results = []
    for query in queries:
        try:
            results = searcher.invoke(query)
            for r in results:
                content = r.get("content", "")
                url = r.get("url", "")
                if content:
                    all_results.append(f"Source: {url}\n{content[:300]}")
        except Exception as e:
            all_results.append(f"Search error: {str(e)}")

    if not all_results:
        return f"No delivery performance data found for '{supplier_name}'."
    return f"Delivery track record for {supplier_name}:\n\n" + "\n\n".join(all_results[:4])
