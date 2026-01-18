#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Detect script location (works for both local run and curl pipe)
if [ -n "$BASH_SOURCE" ] && [ -f "$BASH_SOURCE" ]; then
    SCRIPT_DIR="$(cd "$(dirname "$BASH_SOURCE")" && pwd)"
else
    # Running from curl, install to home directory
    SCRIPT_DIR="$HOME/tg-summarizer"
fi

echo -e "${CYAN}"
echo "╔═══════════════════════════════════════╗"
echo "║     TG Summarizer - Installation      ║"
echo "╚═══════════════════════════════════════╝"
echo -e "${NC}"

# 1. Check Python 3.8+
echo -e "${YELLOW}[1/7] Checking Python...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
        echo -e "  ${GREEN}Python $PYTHON_VERSION${NC}"
    else
        echo -e "  ${RED}Python $PYTHON_VERSION found, but 3.8+ required${NC}"
        echo "  Install Python 3.8+: https://www.python.org/downloads/"
        exit 1
    fi
else
    echo -e "  ${RED}Python 3 not found${NC}"
    echo "  Install Python 3.8+: https://www.python.org/downloads/"
    exit 1
fi

# 2. Check/Install Ollama
echo -e "${YELLOW}[2/7] Checking Ollama...${NC}"
if command -v ollama &> /dev/null; then
    echo -e "  ${GREEN}Ollama installed${NC}"
else
    echo -e "  ${YELLOW}Installing Ollama...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &> /dev/null; then
            brew install ollama
        else
            echo -e "  ${RED}Homebrew not found. Install Ollama manually:${NC}"
            echo "  https://ollama.com/download"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        curl -fsSL https://ollama.com/install.sh | sh
    else
        echo -e "  ${RED}Unsupported OS. Install Ollama manually:${NC}"
        echo "  https://ollama.com/download"
        exit 1
    fi
fi

# 3. Start Ollama if not running
echo -e "${YELLOW}[3/7] Starting Ollama...${NC}"
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "  ${GREEN}Ollama is running${NC}"
else
    echo -e "  ${YELLOW}Starting Ollama service...${NC}"
    ollama serve > /dev/null 2>&1 &
    sleep 3

    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "  ${GREEN}Ollama started${NC}"
    else
        echo -e "  ${RED}Failed to start Ollama. Try manually: ollama serve${NC}"
        exit 1
    fi
fi

# 4. LLM Model Setup
echo -e "${YELLOW}[4/7] LLM Model Setup...${NC}"
echo ""

# Show installed models
INSTALLED_MODELS=$(ollama list 2>/dev/null | tail -n +2 | awk '{print $1}')
if [ -n "$INSTALLED_MODELS" ]; then
    echo "Installed models:"
    echo "$INSTALLED_MODELS" | nl -w2 -s") "
    echo ""
fi

# Model selection menu
echo "Options:"
echo "  1) Use existing model (enter name)"
echo "  2) Download llama3.2 (~2GB, recommended)"
echo "  3) Download qwen2.5:7b (~4.7GB, better quality)"
echo ""
read -p "Choose [1-3, default=2]: " MODEL_CHOICE

case $MODEL_CHOICE in
    1)
        read -p "Enter model name: " MODEL
        if [ -z "$MODEL" ]; then
            MODEL="llama3.2"
            echo -e "  ${YELLOW}No model specified, using llama3.2${NC}"
            ollama pull $MODEL
        fi
        ;;
    3)
        MODEL="qwen2.5:7b"
        if ollama list | grep -q "qwen2.5"; then
            echo -e "  ${GREEN}Model $MODEL already downloaded${NC}"
        else
            echo -e "  ${YELLOW}Downloading $MODEL...${NC}"
            ollama pull $MODEL
        fi
        ;;
    *)
        MODEL="llama3.2"
        if ollama list | grep -q "llama3.2"; then
            echo -e "  ${GREEN}Model $MODEL already downloaded${NC}"
        else
            echo -e "  ${YELLOW}Downloading $MODEL...${NC}"
            ollama pull $MODEL
        fi
        ;;
esac
echo -e "  ${GREEN}Using model: $MODEL${NC}"
export OLLAMA_MODEL=$MODEL

# 5. Setup Python environment
echo -e "${YELLOW}[5/7] Setting up Python environment...${NC}"
cd "$SCRIPT_DIR"

# Create venv if not exists
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

# Activate and install dependencies
source .venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo -e "  ${GREEN}Dependencies installed${NC}"

# 6. Create launcher script
echo -e "${YELLOW}[6/7] Creating launcher...${NC}"
cat > summarize << 'LAUNCHER'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"
source .venv/bin/activate
python summarize.py "$@"
LAUNCHER
chmod +x summarize
echo -e "  ${GREEN}Launcher created${NC}"

# 7. Configure Telegram
echo -e "${YELLOW}[7/7] Configuring Telegram...${NC}"
echo ""
python setup.py

# Done!
echo ""
echo -e "${GREEN}Done!${NC} Run: ${CYAN}./summarize --unread${NC}"
echo ""
