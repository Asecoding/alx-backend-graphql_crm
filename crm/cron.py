import datetime
import requests

def log_crm_heartbeat():
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_message = f"{timestamp} CRM is alive\n"

    # Append to heartbeat log
    with open("/tmp/crm_heartbeat_log.txt", "a") as f:
        f.write(log_message)

    # Optional: GraphQL health check
    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": "{ hello }"},
            timeout=5
        )
        if response.status_code == 200 and "hello" in response.text:
            print("GraphQL endpoint is responsive.")
        else:
            print("GraphQL health check failed.")
    except Exception as e:
        print(f"GraphQL health check error: {e}")

def update_low_stock():
    endpoint = "http://localhost:8000/graphql/"
    query = """
    mutation {
      updateLowStockProducts {
        updatedProducts {
          name
          stock
        }
        message
      }
    }
    """

    try:
        response = requests.post(endpoint, json={'query': query})
        data = response.json()
        updates = data['data']['updateLowStockProducts']['updatedProducts']
        message = data['data']['updateLowStockProducts']['message']

        with open("/tmp/low_stock_updates_log.txt", "a") as log:
            log.write(f"\n[{datetime.now()}] {message}\n")
            for product in updates:
                log.write(f"- {product['name']}: stock={product['stock']}\n")

    except Exception as e:
        with open("/tmp/low_stock_updates_log.txt", "a") as log:
            log.write(f"\n[{datetime.now()}] ERROR: {str(e)}\n")

