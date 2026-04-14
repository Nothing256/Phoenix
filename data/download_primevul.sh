#!/bin/bash
# ==============================================================================
# Download PrimeVul v0.1 Paired Test Set
#
# The PrimeVul dataset is hosted on Google Drive by the original authors.
# This script provides instructions since Google Drive requires browser access.
#
# Source: https://github.com/prem-16/PrimeVul
# Paper:  Ding et al., "Vulnerability Detection with Code Language Models:
#         How Far Are We?", ICSE 2025.
#         DOI: 10.1109/ICSE55347.2025.00038
# ==============================================================================

set -e

TARGET="./primevul_test_paired.jsonl"

if [ -f "$TARGET" ]; then
    echo "✅ PrimeVul data already exists at: $TARGET"
    exit 0
fi

echo "📥 PrimeVul v0.1 Paired Test Set Download"
echo ""
echo "The dataset is hosted on Google Drive:"
echo ""
echo "  🔗 https://drive.google.com/drive/folders/19iLaNDS0z99N8kB_jBRTmDLehwZBolMY"
echo ""
echo "Please download 'primevul_test_paired.jsonl' from the link above"
echo "and place it in this directory:"
echo ""
echo "  $(pwd)/primevul_test_paired.jsonl"
echo ""

# Attempt gdown if available
if command -v gdown &> /dev/null; then
    echo "🔧 gdown detected. Attempting automatic download..."
    echo "   (If this fails, please download manually from the link above.)"
    echo ""
    # Navigate to the folder and find the file to download
    gdown --folder "https://drive.google.com/drive/folders/19iLaNDS0z99N8kB_jBRTmDLehwZBolMY" \
        --output . --remaining-ok 2>/dev/null || {
        echo "⚠️  gdown failed. Please download manually."
        exit 1
    }
    if [ -f "$TARGET" ]; then
        echo "✅ Download complete: $TARGET"
    else
        echo "⚠️  File not found after download. Please check the Google Drive link."
    fi
else
    echo "💡 Tip: Install 'gdown' for command-line Google Drive downloads:"
    echo "   pip install gdown"
    echo ""
    echo "   Then re-run this script."
fi
