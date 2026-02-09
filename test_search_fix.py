
import requests
import sys

BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

def test_search():
    print("Fetching all products...")
    try:
        resp = requests.get(f"{BASE_URL}/product/storefront/api/products/", headers=HEADERS)
        if resp.status_code != 200:
            print(f"Failed to fetch products: {resp.status_code}")
            return False
        
        all_data = resp.json()
        total_count = all_data.get('count', 0)
        results = all_data.get('results', [])
        
        if total_count == 0 or not results:
            print("No products found in DB. Cannot test search.")
            return True # Not a failure of search implementation
            
        print(f"Total products: {total_count}")
        print("Product names available:")
        for p in results[:5]:
            print(f" - {p.get('name')}")
        
        # Pick a search term from the first product
        first_product = results[0]
        name = first_product.get('name', 'Product')
        search_term = name.split()[0] if name else "test"
        
        print(f"Testing search with term: '{search_term}'")
        
        search_url = f"{BASE_URL}/product/storefront/api/products/?search={search_term}"
        print(f"GET {search_url}")
        
        search_resp = requests.get(search_url, headers=HEADERS)
        if search_resp.status_code != 200:
            print(f"Search request failed: {search_resp.status_code}")
            return False
            
        search_data = search_resp.json()
        search_count = search_data.get('count', 0)
        search_results = search_data.get('results', [])
        
        print(f"Search results count: {search_count}")
        
        if search_count == total_count and total_count > 1:
            # It's possible that all products match, but unlikely if we pick a specific word.
            # However, if the issue persists (filtering ignored), search_count will EQUAL total_count.
            # Let's check if the items actually contain the term.
            
            non_matching = [p['name'] for p in search_results if search_term.lower() not in p['name'].lower()]
            if len(non_matching) == len(search_results):
                 print("Failure: Search returned items that do NOT contain the search term.")
                 return False
            
            # If we have a lot of products, validation is trickier without good test data.
            # But the user's issue was "Response body contains all the products".
            pass

        # Verify that referenced results actually contain the term (in name, summary, brand, etc)
        # We search in name, summary, description, category__name, brand
        
        matched_count = 0
        for item in search_results:
            found = False
            # Check name
            if search_term.lower() in item.get('name', '').lower():
                found = True
            # Check summary - logic depends on if summary is in list response. 
            # Default serializer usually has name.
            
            if found:
                matched_count += 1
                
        print(f"Verified {matched_count}/{len(search_results)} items contain '{search_term}' in name.")
        
        if search_count < total_count:
            print("Success: Search successfully filtered the results.")
            return True
        elif search_count == total_count:
            print("Warning: Search count equals total count. This might be correct if all items match, or incorrect if filter is ignored.")
            # If we used a term that shouldn't match everything
            if total_count > 1:
                 # Try a nonsense term
                 nonsense = "xyz123abc"
                 print(f"Testing search with nonsense term: '{nonsense}'")
                 resp_nonsense = requests.get(f"{BASE_URL}/product/storefront/api/products/?search={nonsense}", headers=HEADERS)
                 nonsense_data = resp_nonsense.json()
                 if nonsense_data.get('count', 0) == 0:
                     print("Success: Nonsense search returned 0 results.")
                     return True
                 else:
                     print(f"Failure: Nonsense search returned {nonsense_data.get('count')} results. Filter is likely ignored.")
                     return False
            return True
            
    except Exception as e:
        print(f"Exception: {e}")
        return False

if __name__ == "__main__":
    if test_search():
        sys.exit(0)
    else:
        sys.exit(1)
