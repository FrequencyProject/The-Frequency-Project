import time
import urllib.request

URL = "http://localhost:8080/metrics"

print("Engaging Network-Isolated DSP Spectral Layer...")
print(f"Streaming live metrics from local engine endpoint: {URL}")

while True:
    try:
        # Pull the live mathematical metrics from your running session
        with urllib.request.urlopen(URL, timeout=1) as response:
            html = response.read().decode('utf-8')
            
        print("\n--- [LIVE ENGINE SPECTRAL METRICS] ---")
        lines = html.split('\n')
        for line in lines:
            # Filter and print only the active statistical tracks
            if "vivic_" in line and not line.startswith("#"):
                print(f" -> {line}")
                
    except Exception as e:
        print(f"Waiting for local session engine data link... (Error: {e})")
        
    # Query the live metrics engine 2 times per second
    time.sleep(0.5)
