import http.client

# Loop through multiple connections
for i in range(5):
    # Connect to the server
    conn = http.client.HTTPConnection("localhost", 8080)

    # Send a GET request to the server
    conn.request("GET", "/")

    # Get the response from the server
    res = conn.getresponse()

    # Get the HTTP status code and reason phrase
    status = res.status
    reason = res.reason

    # Print the URL to connect to the server
    print(f"Connect to http://localhost:8080/ to view the server response.\nHTTP Status: {status} {reason}")

    # Close the connection
    conn.close()