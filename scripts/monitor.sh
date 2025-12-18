#!/bin/bash

# Production Monitoring Script for Leaflet Product Extractor
# Monitors application health, performance, and resource usage

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
MONITORING_INTERVAL=${1:-60}  # Default 60 seconds
LOG_FILE="./logs/monitoring.log"
ALERT_THRESHOLD_CPU=80
ALERT_THRESHOLD_MEMORY=85
ALERT_THRESHOLD_DISK=90
HEALTHCHECK_TIMEOUT=10

# Functions
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[OK]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

# Check if services are running
check_services() {
    info "Checking service status..."
    
    local services=("leaflet-backend-prod" "leaflet-frontend-prod" "leaflet-nginx-prod")
    local all_running=true
    
    for service in "${services[@]}"; do
        if docker ps --format "table {{.Names}}" | grep -q "^$service$"; then
            local status=$(docker inspect --format='{{.State.Status}}' "$service")
            local health=$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}' "$service")
            
            if [[ "$status" == "running" ]]; then
                if [[ "$health" == "healthy" ]] || [[ "$health" == "no-healthcheck" ]]; then
                    success "$service: running (health: $health)"
                else
                    warning "$service: running but unhealthy (health: $health)"
                    all_running=false
                fi
            else
                error "$service: not running (status: $status)"
                all_running=false
            fi
        else
            error "$service: container not found"
            all_running=false
        fi
    done
    
    return $([[ "$all_running" == true ]] && echo 0 || echo 1)
}

# Check API endpoints
check_api_health() {
    info "Checking API health..."
    
    # Check backend health
    if curl -f -s --max-time "$HEALTHCHECK_TIMEOUT" http://localhost:8000/health > /dev/null; then
        success "Backend API: healthy"
    else
        error "Backend API: not responding"
        return 1
    fi
    
    # Check frontend
    if curl -f -s --max-time "$HEALTHCHECK_TIMEOUT" http://localhost/ > /dev/null; then
        success "Frontend: healthy"
    else
        error "Frontend: not responding"
        return 1
    fi
    
    # Check API endpoints
    local endpoints=("/api/v1/extractions" "/docs" "/openapi.json")
    for endpoint in "${endpoints[@]}"; do
        if curl -f -s --max-time "$HEALTHCHECK_TIMEOUT" "http://localhost:8000$endpoint" > /dev/null; then
            success "Endpoint $endpoint: accessible"
        else
            warning "Endpoint $endpoint: not accessible"
        fi
    done
    
    return 0
}

# Monitor resource usage
check_resource_usage() {
    info "Checking resource usage..."
    
    # CPU usage
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')
    cpu_usage=${cpu_usage%.*}  # Remove decimal
    
    if [[ $cpu_usage -gt $ALERT_THRESHOLD_CPU ]]; then
        warning "High CPU usage: ${cpu_usage}%"
    else
        success "CPU usage: ${cpu_usage}%"
    fi
    
    # Memory usage
    local memory_info=$(free | grep '^Mem:')
    local total_mem=$(echo $memory_info | awk '{print $2}')
    local used_mem=$(echo $memory_info | awk '{print $3}')
    local memory_percent=$((used_mem * 100 / total_mem))
    
    if [[ $memory_percent -gt $ALERT_THRESHOLD_MEMORY ]]; then
        warning "High memory usage: ${memory_percent}%"
    else
        success "Memory usage: ${memory_percent}%"
    fi
    
    # Disk usage
    local disk_usage=$(df -h . | tail -1 | awk '{print $5}' | sed 's/%//')
    
    if [[ $disk_usage -gt $ALERT_THRESHOLD_DISK ]]; then
        warning "High disk usage: ${disk_usage}%"
    else
        success "Disk usage: ${disk_usage}%"
    fi
    
    # Docker container resource usage
    info "Docker container resource usage:"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" | grep -E "(leaflet|nginx)"
}

# Check log files for errors
check_logs() {
    info "Checking recent logs for errors..."
    
    local log_dirs=("./logs" "./backend/logs")
    local error_patterns=("ERROR" "CRITICAL" "Exception" "Traceback")
    
    for log_dir in "${log_dirs[@]}"; do
        if [[ -d "$log_dir" ]]; then
            for pattern in "${error_patterns[@]}"; do
                local count=$(find "$log_dir" -name "*.log" -mtime -1 -exec grep -c "$pattern" {} + 2>/dev/null | awk '{sum+=$1} END {print sum+0}')
                if [[ $count -gt 0 ]]; then
                    warning "Found $count '$pattern' entries in recent logs"
                fi
            done
        fi
    done
    
    # Check Docker container logs for errors
    local containers=("leaflet-backend-prod" "leaflet-frontend-prod")
    for container in "${containers[@]}"; do
        if docker ps --format "{{.Names}}" | grep -q "^$container$"; then
            local error_count=$(docker logs --since="1h" "$container" 2>&1 | grep -i error | wc -l)
            if [[ $error_count -gt 0 ]]; then
                warning "$container: $error_count errors in last hour"
            fi
        fi
    done
}

# Check performance metrics
check_performance() {
    info "Checking performance metrics..."
    
    # Check if we can get recent extraction data
    local extractions_response=$(curl -s http://localhost:8000/api/v1/extractions?limit=5)
    if [[ $? -eq 0 ]]; then
        local extraction_count=$(echo "$extractions_response" | jq -r '.extractions | length' 2>/dev/null || echo "unknown")
        success "Recent extractions available: $extraction_count"
        
        # Check average processing time if data is available
        if command -v jq > /dev/null && [[ "$extraction_count" != "unknown" ]] && [[ $extraction_count -gt 0 ]]; then
            local avg_time=$(echo "$extractions_response" | jq -r '[.extractions[].processing_time] | add / length' 2>/dev/null || echo "unknown")
            info "Average processing time: ${avg_time}s"
        fi
    else
        error "Unable to retrieve extraction data"
    fi
    
    # Check response times
    local start_time=$(date +%s.%N)
    if curl -f -s http://localhost:8000/health > /dev/null; then
        local end_time=$(date +%s.%N)
        local response_time=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "unknown")
        if [[ "$response_time" != "unknown" ]] && (( $(echo "$response_time > 2" | bc -l) )); then
            warning "Slow API response time: ${response_time}s"
        else
            success "API response time: ${response_time}s"
        fi
    fi
}

# Generate monitoring report
generate_report() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local report_file="./logs/monitoring_report_$(date +%Y%m%d_%H%M%S).json"
    
    info "Generating monitoring report..."
    
    # Collect data
    local services_status=$([[ $(check_services) ]] && echo "healthy" || echo "unhealthy")
    local api_status=$([[ $(check_api_health) ]] && echo "healthy" || echo "unhealthy")
    
    # Create JSON report
    cat > "$report_file" << EOF
{
  "timestamp": "$timestamp",
  "services": {
    "status": "$services_status",
    "containers": [
      $(docker ps --format '{"name":"{{.Names}}","status":"{{.Status}}","ports":"{{.Ports}}"}' | grep leaflet | paste -sd, -)
    ]
  },
  "api": {
    "status": "$api_status"
  },
  "resources": {
    "cpu_usage": "$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')",
    "memory_usage": "$(free | grep '^Mem:' | awk '{printf "%.1f", $3/$2 * 100.0}')%",
    "disk_usage": "$(df -h . | tail -1 | awk '{print $5}')"
  },
  "uptime": "$(uptime -p 2>/dev/null || uptime)"
}
EOF
    
    success "Report generated: $report_file"
}

# Send alerts (placeholder for integration with external systems)
send_alert() {
    local alert_type="$1"
    local message="$2"
    
    warning "ALERT [$alert_type]: $message"
    
    # Here you could integrate with:
    # - Email notifications
    # - Slack/Discord webhooks
    # - PagerDuty
    # - SMS services
    # - Log aggregation systems (ELK, Splunk)
    
    # Example webhook call (uncomment and configure as needed):
    # curl -X POST https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK \
    #   -H 'Content-type: application/json' \
    #   --data '{"text":"Alert: '"$message"'"}'
}

# Main monitoring loop
monitor() {
    log "Starting monitoring (interval: ${MONITORING_INTERVAL}s)"
    
    while true; do
        echo ""
        echo "=== Monitoring Check - $(date) ==="
        
        # Run all checks
        local overall_health=true
        
        if ! check_services; then
            send_alert "SERVICE" "One or more services are not running properly"
            overall_health=false
        fi
        
        if ! check_api_health; then
            send_alert "API" "API health check failed"
            overall_health=false
        fi
        
        check_resource_usage
        check_logs
        check_performance
        
        if [[ "$overall_health" == true ]]; then
            success "Overall system health: OK"
        else
            error "Overall system health: DEGRADED"
        fi
        
        # Generate periodic report (every 10th check)
        local check_count_file="/tmp/monitor_check_count"
        local check_count=1
        if [[ -f "$check_count_file" ]]; then
            check_count=$(cat "$check_count_file")
            check_count=$((check_count + 1))
        fi
        echo "$check_count" > "$check_count_file"
        
        if [[ $((check_count % 10)) -eq 0 ]]; then
            generate_report
        fi
        
        echo "=== End Check ==="
        sleep "$MONITORING_INTERVAL"
    done
}

# One-time health check
health_check() {
    echo "=== Health Check ==="
    
    local overall_health=true
    
    check_services || overall_health=false
    check_api_health || overall_health=false
    check_resource_usage
    check_performance
    
    echo ""
    if [[ "$overall_health" == true ]]; then
        success "✅ System is healthy"
        exit 0
    else
        error "❌ System has issues"
        exit 1
    fi
}

# Usage information
usage() {
    echo "Usage: $0 [OPTIONS] [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  monitor [interval]   Start continuous monitoring (default interval: 60s)"
    echo "  check               Perform one-time health check"
    echo "  report              Generate monitoring report"
    echo "  help                Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 monitor 30       Monitor every 30 seconds"
    echo "  $0 check           Quick health check"
    echo "  $0 report          Generate report"
    echo ""
}

# Main execution
case "${1:-monitor}" in
    "monitor")
        shift
        MONITORING_INTERVAL=${1:-$MONITORING_INTERVAL}
        mkdir -p logs
        monitor
        ;;
    "check")
        health_check
        ;;
    "report")
        mkdir -p logs
        generate_report
        ;;
    "help"|"-h"|"--help")
        usage
        ;;
    *)
        echo "Unknown command: $1"
        usage
        exit 1
        ;;
esac