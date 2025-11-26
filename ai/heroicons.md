# Heroicons Usage Guide

## Overview
This project uses `cotton-heroicons`, a Django Cotton component library for Heroicons. **Always use these components instead of creating custom SVG icons.**

## Package
- **Library**: `cotton-heroicons` (already installed)
- **Documentation**: https://github.com/snopoke/cotton-heroicons
- **Icon Reference**: https://heroicons.com/

## Usage

### Basic Syntax
Use the `<c-heroicon.{icon-name}/>` component tag:

```html
<!-- Default variant is 'outline' -->
<c-heroicon.cloud/>
```

### Variants
Heroicons come in three variants:
- `outline` (default) - 24x24px stroke icons
- `solid` - 24x24px filled icons
- `mini` - 20x20px filled icons

Specify variant using the `variant` attribute:

```html
<c-heroicon.shopping-bag variant="mini"/>
<c-heroicon.user variant="solid"/>
<c-heroicon.pencil variant="outline"/>
```

### Adding Classes
Use the `class` attribute to add Tailwind classes:

```html
<c-heroicon.trash class="h-5 w-5 text-red-600"/>
<c-heroicon.check class="h-6 w-6 text-green-500"/>
```

### Common Examples

```html
<!-- Edit icon -->
<c-heroicon.pencil class="h-5 w-5"/>

<!-- Delete/Trash icon -->
<c-heroicon.trash class="h-5 w-5 text-red-600"/>

<!-- Plus/Add icon -->
<c-heroicon.plus class="h-5 w-5"/>

<!-- Chevron down for dropdowns -->
<c-heroicon.chevron-down class="h-5 w-5"/>

<!-- Check mark -->
<c-heroicon.check class="h-6 w-6 text-green-500"/>

<!-- Warning -->
<c-heroicon.exclamation-triangle class="h-5 w-5 text-yellow-500"/>
```

## Icon Names
Icon names use kebab-case. Common icons include:
- `pencil`, `pencil-square` - Edit actions
- `trash` - Delete actions
- `plus`, `plus-circle` - Add/Create actions
- `chevron-down`, `chevron-up`, `chevron-left`, `chevron-right` - Navigation
- `x-mark` - Close/Cancel
- `check`, `check-circle` - Success/Confirmation
- `exclamation-triangle` - Warnings
- `information-circle` - Info
- `magnifying-glass` - Search
- `cog-6-tooth` - Settings
- `user`, `user-circle` - User profile
- `bars-3` - Menu/Hamburger

Visit https://heroicons.com/ for the complete icon catalog.

## Important Rules
1. **NEVER create custom SVG icons** - Always use cotton-heroicons components
2. **Always use the component syntax** - `<c-heroicon.{name}/>`
3. **Default variant is outline** - Only specify variant if you need solid or mini
4. **Use Tailwind classes** for sizing and colors - e.g., `class="h-5 w-5 text-gray-600"`
