from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults


@tool
def search_supplier_reputation(supplier_name: str) -> str:
    """
    Search the web for a supplier's reputation, customer reviews, complaints,
    quality issues, and any negative press coverage.
    Input: the supplier company name e.g. 'DhakaTextiles Ltd Bangladesh'.
    Returns: summarised reputation findings from web sources.
    """
    searcher = TavilySearchResults(max_results=4)
    queries = [
        f"{supplier_name} reviews complaints quality issues",
        f"{supplier_name} supplier reputation reliability",
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
        return f"No reputation data found for '{supplier_name}'."
    return f"Reputation findings for {supplier_name}:\n\n" + "\n\n".join(all_results[:4])
