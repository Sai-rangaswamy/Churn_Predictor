@echo off
echo Starting ML Service (Port 5000)...
start cmd /k "cd ml-service && python app.py"

echo Starting Go Backend Proxy (Port 8080)...
start cmd /k "cd backend-go && go run main.go"

echo Starting Vue Frontend (Port 5173 or similar)...
start cmd /k "cd frontend\vue-project && npm run dev"

echo All services are starting up in separate windows!
echo Please check the new command prompt windows for any errors.
