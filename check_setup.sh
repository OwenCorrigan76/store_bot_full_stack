#!/bin/bash

# Guitar Store Chatbot - Setup Checklist
# Run this to verify your setup is complete

echo "🎸 Guitar Store Chatbot - Setup Checker"
echo "========================================"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_installed() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 is installed"
        return 0
    else
        echo -e "${RED}✗${NC} $1 is NOT installed"
        return 1
    fi
}

echo "📋 Checking Prerequisites:"
echo ""

check_installed "python3"
check_installed "node"
check_installed "npm"
check_installed "git"

echo ""
echo "📁 Checking Project Structure:"
echo ""

files_to_check=(
    "backend/main.py"
    "backend/models.py"
    "backend/requirements.txt"
    "backend/routers/chat.py"
    "backend/routers/products.py"
    "backend/services/llm.py"
    "backend/services/products.py"
    "backend/services/prompt_builder.py"
    "frontend/package.json"
    "frontend/src/App.tsx"
    "frontend/src/components/ChatInterface.tsx"
    "README.md"
    "QUICK_START.md"
    "ARCHITECTURE.md"
    "DEPLOYMENT.md"
)

missing=0
for file in "${files_to_check[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file (MISSING)"
        ((missing++))
    fi
done

echo ""
echo "📊 Summary:"
echo ""
echo "Total checks: $((${#files_to_check[@]} + 4))"
echo "Missing files: $missing"

if [ $missing -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Setup looks good! Ready to go!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Read QUICK_START.md"
    echo "2. Start vLLM: python -m vllm.entrypoints.openai.api_server --model meta-llama/Llama-2-7b-hf --port 8000"
    echo "3. Start backend: cd backend && uvicorn main:app --reload"
    echo "4. Start frontend: cd frontend && npm run dev"
else
    echo ""
    echo -e "${RED}⚠️  Some files are missing!${NC}"
    echo "Please check your project structure."
fi
