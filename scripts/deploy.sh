#!/bin/bash

# Production Deployment Script for Leaflet Product Extractor
# This script deploys the application to a production environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DEPLOYMENT_ENV=${1:-production}
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
LOG_FILE="./logs/deployment.log"

# Functions
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}ERROR: $1${NC}" | tee -a "$LOG_FILE"
    exit 1
}

success() {
    echo -e "${GREEN}SUCCESS: $1${NC}" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}WARNING: $1${NC}" | tee -a "$LOG_FILE"
}

# Pre-deployment checks
check_prerequisites() {
    log "Starting pre-deployment checks..."
    
    # Check if Docker is installed and running
    if ! docker --version > /dev/null 2>&1; then
        error "Docker is not installed or not running"
    fi
    
    # Check if docker-compose is available
    if ! docker-compose --version > /dev/null 2>&1; then
        error "docker-compose is not installed"
    fi
    
    # Check if required files exist
    local required_files=(
        "docker-compose.prod.yml"
        "backend/Dockerfile.prod"
        "frontend/Dockerfile.prod"
        "backend/.env"
        "frontend/.env"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            error "Required file not found: $file"
        fi
    done
    
    success "Pre-deployment checks passed"
}

# Backup current deployment
backup_current_deployment() {
    log "Creating backup of current deployment..."
    
    mkdir -p "$BACKUP_DIR"
    
    # Backup data directory
    if [[ -d "./data" ]]; then
        cp -r ./data "$BACKUP_DIR/"
        log "Data directory backed up"
    fi
    
    # Backup logs
    if [[ -d "./logs" ]]; then
        cp -r ./logs "$BACKUP_DIR/"
        log "Logs directory backed up"
    fi
    
    # Export current docker images (if any)
    if docker ps -q > /dev/null 2>&1; then
        docker save $(docker images --format "table {{.Repository}}:{{.Tag}}" | grep -E "(leaflet|backend|frontend)" | tr '\n' ' ') > "$BACKUP_DIR/images.tar" 2>/dev/null || true
    fi
    
    success "Backup completed: $BACKUP_DIR"
}

# Build production images
build_images() {
    log "Building production Docker images..."
    
    # Build backend
    log "Building backend image..."
    docker build -f backend/Dockerfile.prod -t leaflet-backend:latest ./backend
    
    # Build frontend
    log "Building frontend image..."
    docker build -f frontend/Dockerfile.prod -t leaflet-frontend:latest ./frontend
    
    success "Images built successfully"
}

# Run tests before deployment
run_tests() {
    log "Running tests before deployment..."
    
    # Backend tests
    log "Running backend tests..."
    cd backend
    if [[ -f "requirements-dev.txt" ]]; then
        pip install -r requirements-dev.txt > /dev/null 2>&1 || true
    fi
    python -m pytest tests/ --tb=short || error "Backend tests failed"
    cd ..
    
    # Frontend tests
    log "Running frontend tests..."
    cd frontend
    npm test -- --coverage --watchAll=false || error "Frontend tests failed"
    cd ..
    
    success "All tests passed"
}

# Deploy services
deploy_services() {
    log "Deploying services..."
    
    # Stop existing services
    docker-compose -f docker-compose.prod.yml down || true
    
    # Start new services
    docker-compose -f docker-compose.prod.yml up -d --build
    
    # Wait for services to be healthy
    log "Waiting for services to be ready..."
    sleep 30
    
    # Check backend health
    local max_retries=10
    local retry=0
    
    while [[ $retry -lt $max_retries ]]; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            success "Backend is healthy"
            break
        fi
        
        retry=$((retry + 1))
        log "Waiting for backend... (attempt $retry/$max_retries)"
        sleep 10
    done
    
    if [[ $retry -eq $max_retries ]]; then
        error "Backend failed to start properly"
    fi
    
    # Check frontend health
    if curl -f http://localhost > /dev/null 2>&1; then
        success "Frontend is healthy"
    else
        warning "Frontend health check failed, but continuing..."
    fi
    
    success "Deployment completed successfully"
}

# Post-deployment verification
verify_deployment() {
    log "Running post-deployment verification..."
    
    # Check container status
    local containers=$(docker-compose -f docker-compose.prod.yml ps -q)
    for container in $containers; do
        local status=$(docker inspect --format='{{.State.Status}}' "$container")
        if [[ "$status" != "running" ]]; then
            error "Container $container is not running (status: $status)"
        fi
    done
    
    # Test API endpoints
    log "Testing API endpoints..."
    
    # Test health endpoint
    if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
        error "Health endpoint not responding"
    fi
    
    # Test extractions endpoint
    if ! curl -f http://localhost:8000/api/v1/extractions > /dev/null 2>&1; then
        error "Extractions endpoint not responding"
    fi
    
    # Check disk space
    local disk_usage=$(df -h . | tail -1 | awk '{print $5}' | sed 's/%//')
    if [[ $disk_usage -gt 90 ]]; then
        warning "Disk usage is high: ${disk_usage}%"
    fi
    
    success "Post-deployment verification completed"
}

# Cleanup old images and containers
cleanup() {
    log "Cleaning up old images and containers..."
    
    # Remove dangling images
    docker image prune -f
    
    # Remove unused containers
    docker container prune -f
    
    # Remove old backups (keep last 5)
    if [[ -d "./backups" ]]; then
        find ./backups -maxdepth 1 -type d | sort | head -n -5 | xargs rm -rf
    fi
    
    success "Cleanup completed"
}

# Print deployment summary
print_summary() {
    log "Deployment Summary:"
    echo -e "\n${GREEN}=== DEPLOYMENT SUCCESSFUL ===${NC}"
    echo -e "Environment: ${YELLOW}$DEPLOYMENT_ENV${NC}"
    echo -e "Backend URL: ${YELLOW}http://localhost:8000${NC}"
    echo -e "Frontend URL: ${YELLOW}http://localhost${NC}"
    echo -e "API Docs: ${YELLOW}http://localhost:8000/docs${NC}"
    echo -e "Backup Location: ${YELLOW}$BACKUP_DIR${NC}"
    echo -e "Log File: ${YELLOW}$LOG_FILE${NC}"
    echo ""
    echo "To view logs: docker-compose -f docker-compose.prod.yml logs -f"
    echo "To stop services: docker-compose -f docker-compose.prod.yml down"
    echo ""
}

# Main deployment flow
main() {
    log "Starting production deployment for $DEPLOYMENT_ENV environment"
    
    # Create logs directory
    mkdir -p logs
    
    # Run deployment steps
    check_prerequisites
    backup_current_deployment
    run_tests
    build_images
    deploy_services
    verify_deployment
    cleanup
    print_summary
    
    success "Deployment completed successfully!"
}

# Handle script interruption
trap 'error "Deployment interrupted"' INT TERM

# Run main function
main "$@"