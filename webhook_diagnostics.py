"""
Webhook Diagnostics - Check why webhook isn't processing payments
"""

import requests
import json

def test_webhook_endpoint():
    """Test if webhook endpoint is accessible"""
    print("=" * 80)
    print("Webhook Endpoint Diagnostics")
    print("=" * 80)
    
    # Test local endpoint
    local_url = "http://localhost:5000/razorpay-webhook"
    
    print(f"\n1. Testing local endpoint: {local_url}")
    try:
        # Send a test payload
        test_payload = {
            "entity": "event",
            "event": "payment.captured",
            "payload": {
                "payment": {
                    "entity": {
                        "id": "pay_test",
                        "amount": 500,
                        "description": "35456",  # Order ID
                        "notes": {}
                    }
                }
            }
        }
        
        response = requests.post(local_url, json=test_payload, timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
        if response.status_code == 200:
            print("   [OK] Endpoint is accessible locally")
        else:
            print(f"   [WARN] Unexpected status: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("   [FAIL] Cannot connect - Flask server might not be running")
        print("   [FIX] Start Flask server: python main.py")
    except Exception as e:
        print(f"   [ERROR] {type(e).__name__}: {e}")
    
    print("\n" + "=" * 80)
    print("Common Issues:")
    print("=" * 80)
    print("\n1. Webhook URL not accessible from internet")
    print("   - Razorpay needs to reach your server")
    print("   - If running locally, use ngrok or similar tunnel")
    print("   - Example: ngrok http 5000")
    print("   - Then use: https://your-ngrok-url.ngrok.io/razorpay-webhook")
    
    print("\n2. Payment description doesn't contain order ID")
    print("   - Razorpay payment description must have: '35456' or 'SO-05206'")
    print("   - Check Razorpay dashboard for payment details")
    
    print("\n3. Webhook event not enabled")
    print("   - In Razorpay dashboard, enable 'payment.captured' event")
    print("   - Settings > Webhooks > Configure webhook")
    
    print("\n4. Webhook signature verification")
    print("   - If enabled, ensure webhook secret is configured correctly")
    
    print("\n" + "=" * 80)
    print("Next Steps:")
    print("=" * 80)
    print("1. Check Flask server logs for any webhook calls")
    print("2. Verify webhook URL in Razorpay dashboard")
    print("3. Test webhook manually with order 35456")
    print("4. Check if payment description contains order ID")

if __name__ == "__main__":
    test_webhook_endpoint()

