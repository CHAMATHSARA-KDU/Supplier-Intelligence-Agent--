from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults


@tool
def search_geopolitical_risk(country_or_region: str) -> str:
    """
    Search for geo-political risks in the supplier's country or region.
    Looks for political instability, sanctions, trade restrictions,
    labour strikes, natural disasters, or export bans.
    Input: country or region name e.g. 'Bangladesh' or 'Shenzhen China'.
    Returns: current risk signals from web sources.
    """
    searcher = TavilySearchResults(max_results=4)
    queries = [
        f"{country_or_region} political instability labour unrest 2025",
        f"{country_or_region} trade sanctions export restrictions supply chain risk",
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
        return f"No significant geo-political risk signals found for '{country_or_region}'."
    return f"Geo-political risk findings for {country_or_region}:\n\n" + "\n\n".join(all_results[:4])
