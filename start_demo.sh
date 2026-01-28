#!/bin/bash

# Kill any existing processes on ports 3000, 8000, 8182, 8183 to ensure clean start
lsof -ti :3000,8000,8182,8183 | xargs kill -9 2>/dev/null

echo "Starting Store A (Budget Mart) on port 8182..."
../mock-server/.venv/bin/python server.py --products_db_path=store_a.db --transactions_db_path=store_a_trans.db --port=8182 > store_a.log 2>&1 &

echo "Starting Store B (Premium Grocers) on port 8183..."
../mock-server/.venv/bin/python server.py --products_db_path=store_b.db --transactions_db_path=store_b_trans.db --port=8183 > store_b.log 2>&1 &

echo "Starting Recipe Agent on port 8000..."
cd ../  # Go back to root
recipe-agent/.venv/bin/uvicorn recipe-agent.main:app --port 8000 > agent.log 2>&1 &

echo "Starting Frontend on port 3000..."
cd frontend
python3 -m http.server 3000 > frontend.log 2>&1 &

echo "All services started!"
echo "------------------------------------------------"
echo "OPEN THIS LINK TO DEMO: http://localhost:3000"
echo "------------------------------------------------"
