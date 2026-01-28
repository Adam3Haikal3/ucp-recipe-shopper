#!/bin/bash

# Initialize Data
echo "Initializing Store A..."
python3 mock-server/import_csv.py --products_db_path=store_a.db --transactions_db_path=store_a_trans.db --data_dir=mock-server/data/store_a

echo "Initializing Store B..."
python3 mock-server/import_csv.py --products_db_path=store_b.db --transactions_db_path=store_b_trans.db --data_dir=mock-server/data/store_b

# Start processes in background
echo "Starting Store A (8182)..."
python3 mock-server/server.py --products_db_path=store_a.db --transactions_db_path=store_a_trans.db --port=8182 &

echo "Starting Store B (8183)..."
python3 mock-server/server.py --products_db_path=store_b.db --transactions_db_path=store_b_trans.db --port=8183 &

echo "Starting Recipe Agent (8000)..."
uvicorn recipe-agent.main:app --port 8000 &

echo "Starting Frontend (3000)..."
cd frontend
python3 -m http.server 3000 &

# Wait for any process to exit
wait -n
