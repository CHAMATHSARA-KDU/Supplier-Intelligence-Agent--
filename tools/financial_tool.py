from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults


@tool
def search_financial_health(supplier_name: str) -> str:
    """
    Search for a supplier's financial health — bankruptcy news, funding rounds,
    financial losses, stability indicators, or company closure news.
    Input: the supplier company name.
    Returns: financial health findings from web sources.
    """
    searcher = TavilySearchResults(max_results=4)
    queries = [
        f"{supplier_name} financial health bankruptcy insolvency",
        f"{supplier_name} company financial stability funding",
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
        return f"No financial health data found for '{supplier_name}'."
    return f"Financial health findings for {supplier_name}:\n\n" + "\n\n".join(all_results[:4])
