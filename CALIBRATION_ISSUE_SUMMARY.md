# 🔍 Calibration Issue Analysis - macOS

## Problem Identified ✅

The test calibration shows a **blank window on macOS** because the calibration coordinates are **completely outside the Chrome window**.

## Root Cause 🎯

**Current Chrome window**: Position (120, 67), Size 1440x810
**Calibrated winner region**: Position (1568, 755), Size 100x70

❌ **The winner region is at X=1568, but Chrome only extends to X=1560 (120+1440)**

This means the bot is trying to capture a region that's literally outside the Chrome window, resulting in:
- Empty OCR results 
- Solid colored images (as confirmed by test_current_calibration.png)
- "Blank" preview windows

## Evidence 📸

1. **Chrome detection works**: ✅ Browser detected at (120, 67)
2. **Regions are outside Chrome**: ❌ Winner region at (1568, 755) > Chrome width (1560)
3. **Captured image confirms**: 🖼️ Solid orange image (outside content area)

## Solutions 🔧

### Option 1: Complete Recalibration (Recommended)
```bash
source venv/bin/activate
python roullebot.py --mode calibrate
# Select option 1: "Calibración visual completa"
```

### Option 2: Use Different Chrome Size
The calibration might have been done with Chrome in fullscreen or larger size. Try:
- Making Chrome fullscreen
- Or making Chrome larger to match original calibration

### Option 3: Auto-Fix (if available)
The bot attempted auto-adjustment but detected Chrome is in same position. This suggests the calibration was done on a different setup entirely.

## Why This Happened 🤔

Most likely causes:
1. **Different screen resolution** when calibrating vs now
2. **Chrome was fullscreen** during calibration, now it's windowed
3. **DPI scaling differences** between calibration and current session
4. **Calibration was done on different monitor** setup

## Current Status 📊

- ✅ **All dependencies working** (Tesseract, OpenCV, etc.)
- ✅ **Chrome detection working** 
- ✅ **macOS compatibility confirmed**
- ❌ **Calibration coordinates incorrect for current setup**

## Next Steps 👉

1. **Backup current calibration** (it's in `/Users/alvinnunez/Library/Application Support/roullebot/calibration.json`)
2. **Run option 1** from calibration menu to recalibrate completely
3. **Ensure Chrome is in same position/size** when using the bot as when calibrating

The "blank window" issue on macOS was actually a **calibration mismatch**, not a macOS-specific OpenCV problem!