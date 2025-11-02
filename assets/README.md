# Assets Directory

## Required Files

### Watermark Logo
Place the Uniswap logo here as `uniswap_logo.png`

**Requirements:**
- Format: PNG with transparency
- Recommended size: 200x200px to 400x400px
- Transparent background
- High resolution for quality

**Where to get it:**
- Official Uniswap brand assets: https://uniswap.org/branding
- Or download from: https://github.com/Uniswap/brand-assets

### Installation:
```bash
# Download Uniswap logo
curl -o assets/uniswap_logo.png https://raw.githubusercontent.com/Uniswap/brand-assets/main/logo/uniswap-unicorn-logo.png

# Or if you have the file locally:
cp /path/to/your/uniswap-logo.png assets/uniswap_logo.png
```

## Testing Without Logo

If you don't have the logo yet, the watermark tool will gracefully skip watermarking and return the original video. The bot will still work perfectly for testing!
