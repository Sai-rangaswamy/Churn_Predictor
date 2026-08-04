@echo off
echo Installing Frontend Dependencies...
cd frontend\vue-project
call npm install
cd ..\..

echo.
echo Installing Backend Dependencies...
cd backend-go
call go mod download
cd ..

echo.
echo Installing ML Service Dependencies...
cd ml-service
call pip install flask pandas joblib matplotlib scikit-learn
cd ..

echo.
echo All dependencies installed successfully!
pause
