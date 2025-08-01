#!/bin/bash
set -e  # Exit the script if any command fails

echo "📁 Switching to the RAG project directory"
cd "$(dirname "$0")"

# Check for environment variable file
if [ ! -f ".env" ]; then
    echo "📝 Copying environment variable file..."
    cp env.example .env
    echo "✅ .env file created. Please review and update the configuration"
fi

echo "🚀 Starting the RAG system..."
# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found"
    exit 1
fi

echo "🧹 Stopping and removing old containers"
docker compose down
docker compose build backend

# Create necessary directories
echo "📁 Creating required directories..."
mkdir -p documents faiss_data logs mariadb_data models ollama

# Start MariaDB service
echo "🗄️ Starting MariaDB database service..."
docker compose up -d mariadb

# Check if the database is running properly
echo "🔍 Checking database status..."
for i in {1..30}; do
    if docker compose exec -T mariadb mysql -u rag_user -prag_password_2024 -e "SELECT 1;" > /dev/null 2>&1; then
        echo "✅ Database is up and running"
        break
    else
        echo "⏳ Waiting for the database to start... ($i/30)"
        sleep 1
    fi

    if [ $i -eq 30 ]; then
        echo "❌ Database startup timed out. Please check the logs."
        docker compose logs mariadb
        exit 1
    fi
done

# Start other services
echo "🚀 Starting other services..."
# docker compose build
docker compose up -d

# Display service status
echo "📊 Service status:"
docker compose ps

# Test database connection
echo "🧪 Testing database connection..."
if docker compose exec rag python test_db_connection.py; then
    echo "✅ Database connection test passed"
else
    echo "⚠️ Database connection test failed, but the system can still run"
fi

echo ""
echo "🎉 RAG system started successfully!"
echo "📱 Frontend: http://localhost:8080"
echo "🗄️ Database: localhost:3306"
echo "📊 View logs: docker compose logs -f"
echo "🛑 Stop services: docker compose down"
