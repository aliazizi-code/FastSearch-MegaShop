#!/bin/sh

# Wait for Elasticsearch to become fully ready
echo "[*] Waiting for Elasticsearch to become ready..."
while true; do
  if curl -fs http://elasticsearch:9200/_cluster/health >/dev/null; then
    status=$(curl -fs http://elasticsearch:9200/_cluster/health | grep -oE '"status":"(green|yellow)"')
    if [ -n "$status" ]; then
      break
    fi
  fi
  echo "[-] Elasticsearch not ready yet. Retrying in 10 seconds..."
  sleep 10
done

echo "[✔] Elasticsearch is ready!"

# Register snapshot repository
echo "[*] Registering snapshot repository..."
curl -fs -X PUT http://elasticsearch:9200/_snapshot/my_backup_repo \
  -H 'Content-Type: application/json' \
  -d '{
    "type": "fs",
    "settings": {
      "location": "/snapshots",
      "compress": true
    }
  }'

# Find latest snapshot
echo "[*] Searching for available snapshots..."
SNAPSHOT=$(curl -fs http://elasticsearch:9200/_snapshot/my_backup_repo/_all \
  | grep -oE '"snapshot":"[^"]+"' \
  | cut -d'"' -f4 \
  | sort -r \
  | head -n1)

if [ -n "$SNAPSHOT" ]; then
  echo "[*] Found snapshot: $SNAPSHOT"
  echo "[*] Restoring snapshot..."
  
  # Initiate restore process
  response=$(curl -fs -X POST "http://elasticsearch:9200/_snapshot/my_backup_repo/$SNAPSHOT/_restore" \
    -H 'Content-Type: application/json' \
    -d '{"include_global_state": false}')
  
  if [ $? -eq 0 ]; then
    echo "[✔] Restore process started successfully!"
    echo "    • This may take several minutes to hours depending on size"
    echo "    • Check Elasticsearch logs for detailed progress"
  else
    echo "[!] Failed to start restore process"
    echo "    Server response: $response"
  fi
else
  echo "[!] No valid snapshots found in /snapshots directory"
  echo "    • Ensure snapshot files exist in the mounted volume"
fi