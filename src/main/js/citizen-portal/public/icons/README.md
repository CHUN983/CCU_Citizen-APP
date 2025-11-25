# PWA App Icons

## 📱 Required Icon Sizes

For a complete PWA experience, please provide icons in the following sizes:

- 72x72 pixels - `icon-72x72.png`
- 96x96 pixels - `icon-96x96.png`
- 128x128 pixels - `icon-128x128.png`
- 144x144 pixels - `icon-144x144.png`
- 152x152 pixels - `icon-152x152.png`
- 192x192 pixels - `icon-192x192.png`
- 384x384 pixels - `icon-384x384.png`
- 512x512 pixels - `icon-512x512.png`

## 🎨 Design Guidelines

1. **Simple & Clear**: Icon should be recognizable at small sizes
2. **Safe Zone**: Keep important content within 80% of the icon area
3. **Consistent**: Use the brand color scheme (#409eff)
4. **Transparent Background**: Use PNG with transparency
5. **Square Format**: Icons should be square (1:1 aspect ratio)

## 🛠️ How to Generate Icons

### Option 1: Online Tool (Easiest)
1. Visit: https://www.pwabuilder.com/imageGenerator
2. Upload your base icon (at least 512x512 PNG)
3. Download the generated icon package
4. Replace files in this directory

### Option 2: ImageMagick (Command Line)
```bash
# Install ImageMagick first
# Then run from your base 512x512 icon:
convert icon-512x512.png -resize 72x72 icon-72x72.png
convert icon-512x512.png -resize 96x96 icon-96x96.png
convert icon-512x512.png -resize 128x128 icon-128x128.png
convert icon-512x512.png -resize 144x144 icon-144x144.png
convert icon-512x512.png -resize 152x152 icon-152x152.png
convert icon-512x512.png -resize 192x192 icon-192x192.png
convert icon-512x512.png -resize 384x384 icon-384x384.png
```

### Option 3: Photoshop/Figma/Sketch
Export your design at each required size

## 📦 Current Status

⚠️ **Placeholder icons needed**: Please add your custom app icons to this directory.

For now, you can use a temporary icon generator or the Vite logo as a placeholder.

## 🔗 Resources

- [PWA Icon Guidelines](https://web.dev/add-manifest/#icons)
- [PWA Builder Image Generator](https://www.pwabuilder.com/imageGenerator)
- [Maskable Icon Editor](https://maskable.app/editor)
