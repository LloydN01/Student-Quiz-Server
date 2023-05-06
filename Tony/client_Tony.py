import http.client

# List of IP addresses to simulate multiple clients
ips = ["192.168.0.1", "192.168.0.2", "192.168.0.3", "192.168.0.4", "192.168.0.5"]

# Loop through multiple connections
for ip in ips:
    # Connect to the server with a specific IP address
    conn = http.client.HTTPConnection(ip, 8080)

    # Send a GET request to the server
    conn.request("GET", "/")

    # Get the response from the server
    res = conn.getresponse()

    # Get the HTTP status code and reason phrase
    status = res.status
    reason = res.reason

    # Print the URL to connect to the server
    print(f"Connect to http://{ip}:8080/ to view the server response.\nHTTP Status: {status} {reason}")

    # Close the connection
    conn.close()
