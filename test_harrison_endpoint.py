"""
Test the /test-odoo endpoint with Harrison products
"""

import requests
import sys

def test_harrison_order(order_id):
    """Test endpoint with Harrison order"""
    url = f"http://localhost:5000/test-odoo?order_id={order_id}"
    
    print("=" * 80)
    print(f"Testing Endpoint with Order: {order_id}")
    print("=" * 80)
    print(f"URL: {url}\n")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n[OK] Success: {data.get('message', 'N/A')}")
            print(f"Sale Order ID: {data.get('sale_order_id', 'N/A')}")
            print(f"\nProducts:")
            
            for product in data.get('products', []):
                print(f"\n  Product: {product.get('product_name', 'N/A')}")
                print(f"  Line Name: {product.get('line_name', 'N/A')}")
                print(f"  Detected Type: {product.get('detected_type', 'N/A')}")
                
                detected_type = product.get('detected_type', '').upper()
                if 'HARRISON' in detected_type or 'HARRASON' in detected_type:
                    print(f"  [OK] Correctly detected as HARRISON product!")
                elif 'DISC' in detected_type:
                    print(f"  [WARN] Detected as DISC (might be wrong if this is Harrison)")
                else:
                    print(f"  [WARN] Type unclear: {detected_type}")
        else:
            print(f"[FAIL] Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to Flask server!")
        print("Make sure Flask server is running: python main.py")
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        order_id = sys.argv[1]
        test_harrison_order(order_id)
    else:
        print("Usage: python test_harrison_endpoint.py [order_id]")
        print("\nExample: python test_harrison_endpoint.py 35456")
        print("\nTo find Harrison orders, run: python find_harrison_orders.py")

