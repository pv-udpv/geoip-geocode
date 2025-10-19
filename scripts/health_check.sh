#!/bin/bash
# Health check script for geoip-geocode project
# This script verifies that everything is set up correctly

set -e

echo "🔍 geoip-geocode Health Check"
echo "=============================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check counters
PASSED=0
FAILED=0
WARNINGS=0

# Function to print success
print_success() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED++))
}

# Function to print error
print_error() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED++))
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

# Check Python version
echo "1. Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 8 ]; then
        print_success "Python $PYTHON_VERSION (>= 3.8 required)"
    else
        print_error "Python $PYTHON_VERSION (>= 3.8 required)"
    fi
else
    print_error "Python 3 not found"
fi
echo ""

# Check uv installation
echo "2. Checking package manager..."
if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version | cut -d' ' -f2)
    print_success "uv $UV_VERSION installed"
else
    print_warning "uv not found (using pip instead)"
fi
echo ""

# Check virtual environment
echo "3. Checking virtual environment..."
if [ -d ".venv" ]; then
    print_success "Virtual environment exists"
else
    print_warning "Virtual environment not found (run: uv sync --all-extras)"
fi
echo ""

# Check project structure
echo "4. Checking project structure..."
REQUIRED_DIRS=(
    "src/geoip_geocode"
    "src/geoip_geocode/providers"
    "tests"
    "examples"
    "config"
    "docs"
    "data/databases"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        print_success "Directory $dir exists"
    else
        print_error "Directory $dir missing"
    fi
done
echo ""

# Check key files
echo "5. Checking key files..."
REQUIRED_FILES=(
    "pyproject.toml"
    "README.md"
    "QUICKSTART.md"
    "src/geoip_geocode/__init__.py"
    "src/geoip_geocode/cli.py"
    "src/geoip_geocode/models.py"
    "src/geoip_geocode/config.py"
    "src/geoip_geocode/registry.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "File $file exists"
    else
        print_error "File $file missing"
    fi
done
echo ""

# Check configuration examples
echo "6. Checking configuration examples..."
CONFIG_FILES=(
    ".env.example"
    "config/config.yaml.example"
)

for file in "${CONFIG_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "Config example $file exists"
    else
        print_warning "Config example $file missing"
    fi
done
echo ""

# Check dependencies
echo "7. Checking Python dependencies..."
if [ -d ".venv" ]; then
    if command -v uv &> /dev/null; then
        # Check if packages are installed via uv
        if [ -f "uv.lock" ]; then
            print_success "Dependencies locked (uv.lock exists)"
        else
            print_warning "No uv.lock file (run: uv sync --all-extras)"
        fi
    else
        print_warning "Cannot verify dependencies (uv not installed)"
    fi
else
    print_warning "Cannot verify dependencies (no virtual environment)"
fi
echo ""

# Check database directory
echo "8. Checking database directory..."
if [ -d "data/databases" ]; then
    DB_COUNT=$(find data/databases -name "*.mmdb" -o -name "*.BIN" 2>/dev/null | wc -l)
    if [ "$DB_COUNT" -gt 0 ]; then
        print_success "Found $DB_COUNT database file(s)"
    else
        print_warning "No database files found in data/databases/"
        echo "   Download GeoLite2-City.mmdb or IP2Location BIN files"
    fi
else
    print_error "Database directory not found"
fi
echo ""

# Run tests if available
echo "9. Running tests..."
if [ -d ".venv" ] && [ -d "tests" ]; then
    if command -v uv &> /dev/null; then
        if uv run pytest --tb=no --no-header -q 2>/dev/null; then
            print_success "All tests passed"
        else
            print_error "Some tests failed (run: uv run pytest)"
        fi
    else
        print_warning "Cannot run tests (uv not available)"
    fi
else
    print_warning "Cannot run tests (missing .venv or tests/)"
fi
echo ""

# Check CLI availability
echo "10. Checking CLI..."
if [ -d ".venv" ]; then
    if command -v uv &> /dev/null; then
        if uv run geoip-geocode --help &> /dev/null; then
            print_success "CLI command available"
        else
            print_error "CLI command not available"
        fi
    else
        print_warning "Cannot verify CLI (uv not available)"
    fi
else
    print_warning "Cannot verify CLI (no virtual environment)"
fi
echo ""

# Summary
echo "=============================="
echo "📊 Health Check Summary"
echo "=============================="
echo -e "${GREEN}Passed:${NC} $PASSED"
echo -e "${YELLOW}Warnings:${NC} $WARNINGS"
echo -e "${RED}Failed:${NC} $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    if [ $WARNINGS -eq 0 ]; then
        echo -e "${GREEN}🎉 Everything is working perfectly!${NC}"
        exit 0
    else
        echo -e "${YELLOW}⚠️  Project is functional but has some warnings${NC}"
        echo ""
        echo "Common fixes:"
        echo "  - Install dependencies: uv sync --all-extras"
        echo "  - Download database: geoip-geocode update-db --license-key YOUR_KEY"
        exit 0
    fi
else
    echo -e "${RED}❌ Some critical issues found${NC}"
    echo ""
    echo "Please fix the errors above before proceeding."
    exit 1
fi
