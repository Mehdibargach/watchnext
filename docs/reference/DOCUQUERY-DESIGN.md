# DocuQuery AI — Design System

> Internal reference for Claude Code. Not visible in the app.

---

## Color Tokens

All colors are defined as HSL triplets in `src/index.css` using CSS custom properties.  
Theme is toggled via `data-theme="light"` on `<html>` (dark is default / `:root`).

| Token               | Dark (default)              | Light                        |
|----------------------|-----------------------------|------------------------------|
| `--background`       | `240 4% 4%` (#0A0A0B)      | `0 0% 98%` (#FAFAFA)        |
| `--surface`          | `240 3% 8%` (#141415)      | `0 0% 100%` (#FFFFFF)       |
| `--border-color`     | `240 2% 12%` (#1E1E20)     | `240 6% 90%` (#E4E4E7)     |
| `--foreground`       | `240 5% 93%` (#EDEDEF)     | `240 10% 4%` (#09090B)     |
| `--muted-foreground` | `240 4% 46%` (#71717A)     | `240 4% 46%` (#71717A)     |
| `--accent`           | `239 84% 67%` (#6366F1)    | same                         |
| `--accent-hover`     | `234 89% 74%` (#818CF8)    | same                         |
| `--success`          | `142 71% 45%` (#22C55E)    | same                         |
| `--error`            | `0 84% 60%` (#EF4444)      | same                         |
| `--primary`          | = `--accent`                | same                         |
| `--primary-foreground` | `0 0% 100%` (#FFFFFF)    | same                         |
| `--secondary`        | `240 2% 12%`               | `240 6% 90%`                |
| `--muted`            | `240 2% 12%`               | `240 6% 90%`                |
| `--card`             | = `--surface`               | `0 0% 100%`                 |
| `--border`           | = `--border-color`          | = `--border-color` (light)  |
| `--ring`             | = `--accent`                | same                         |

### Accent usage rule

The accent color (#6366F1 indigo) is **only** used for:
- Interactive elements (buttons, links on hover, focus rings)
- Active/selected indicators (stepper dot, source card border, drag zone)
- Subtle badges (`hsl(var(--accent) / 0.12)` background + accent text)

Static text, headings, and metrics always use `--foreground` or `--muted-foreground`.

---

## Typography

Loaded via Google Fonts in `index.css`:

| Role        | Font Family                            | Weights       | Usage                                 |
|-------------|----------------------------------------|---------------|---------------------------------------|
| UI / Body   | **Inter**                              | 300–700       | All text, headings, labels            |
| Code / Data | **Geist Mono** (fallback: JetBrains Mono) | 400, 500   | Filenames, latency, chunk scores, badges |

### Text sizes used

| Class / Size | Where                                    |
|-------------|------------------------------------------|
| `text-2xl`  | About page h1, eval metric values        |
| `text-xl`   | Upload zone h1                           |
| `text-lg`   | About page h2 sections                   |
| `text-base` | About subtitle, author name              |
| `text-sm`   | Body text, messages, stepper labels       |
| `text-xs`   | Badges, meta info, uppercase labels       |
| `text-[10px]` | Score badge in source cards             |

---

## Spacing & Layout Conventions

| Element            | Pattern                                    |
|--------------------|--------------------------------------------|
| Header             | `h-12`, `px-5`, flex between               |
| Upload zone        | `max-w-md`, centered vertically            |
| About page         | `max-w-3xl`, `px-6`, `py-16`              |
| Chat messages      | `px-4 py-4`, `gap-4` between messages      |
| Input bar          | `px-4 py-3`, `gap-3`, border-t             |
| Source cards        | `gap-2`, `px-3 py-2`, min-w 220px         |
| Section spacing    | `mt-12` between About sections             |

---

## Patterns d'interaction

### Hover states
All hover interactions use **inline style swapping** via `onMouseEnter`/`onMouseLeave`:
- Suggestion chips: border → accent, text → accent
- Theme toggle: bg → surface, color → foreground
- Copy button: muted → foreground
- Source cards: border → accent/0.5
- Send button: accent → accent-hover

### Focus
- Textarea: border-color swaps to accent on focus (inline style)
- No focus ring utilities used directly — custom inline approach

### Transitions
- CSS `transition-colors` on most interactive elements
- Source card `max-width` animates via inline `transition: max-width 0.2s ease`
- Drag zone: `transition-colors duration-150`

### Drag & Drop
- `UploadZone` handles `onDragOver`, `onDragLeave`, `onDrop`
- Visual feedback: dashed border → accent color, bg → accent/0.05

---

## Icons

All from **Lucide React** (`lucide-react` v0.462.0):

| Icon          | Usage                          |
|---------------|--------------------------------|
| `Sun`         | Theme toggle (dark mode)       |
| `Moon`        | Theme toggle (light mode)      |
| `ArrowUp`     | Send button                    |
| `ArrowLeft`   | About page back link           |
| `Check`       | Stepper done state, copy done  |
| `X`           | Error banner, change file btn  |
| `FileText`    | Source card icon                |
| `Copy`        | AI bubble copy button          |
| `RotateCcw`   | New chat button                |
| `Zap`         | Latency indicator              |
| `ChevronDown` | Source card collapsed           |
| `ChevronUp`   | Source card expanded            |

---

## Logo

Custom inline SVG (18×18) in the header:

```svg
<svg width="18" height="18" viewBox="0 0 18 18" fill="none">
  <!-- Back document -->
  <rect x="4" y="5" width="9" height="11" rx="1.5"
        stroke="currentColor" strokeWidth="1.4" />
  <!-- Front document -->
  <rect x="6" y="2" width="9" height="11" rx="1.5"
        fill="hsl(var(--background))" stroke="currentColor" strokeWidth="1.4" />
  <!-- Accent dot -->
  <circle cx="14.5" cy="3.5" r="2.5" fill="hsl(var(--accent))" />
</svg>
```

Two overlapping document shapes (stroke only) with an indigo accent dot in the top-right corner. The logo inherits `--muted-foreground` for strokes.

---

## Animations

| Name            | Definition                                        | Usage                    |
|-----------------|---------------------------------------------------|--------------------------|
| `animate-spin`  | Tailwind built-in                                 | `Spinner` SVG            |
| `animate-bounce`| Tailwind built-in, custom delay/duration          | `SkeletonLoader` dots    |
| `animate-blink` | Custom keyframe in `index.css` (step-end)         | Not currently used       |
| Accordion       | `accordion-down` / `accordion-up` (Radix height) | shadcn accordion         |

### SkeletonLoader timing
3 dots with `animationDelay: 0ms, 160ms, 320ms` and `animationDuration: 1.2s`.

---

## Utility classes (custom)

Defined in `@layer utilities` in `index.css`:

- `.bg-surface` — `hsl(var(--surface))`
- `.border-border-color` — `hsl(var(--border-color))`
- `.text-accent` / `.bg-accent` — accent color
- `.text-accent-hover` / `.bg-accent-hover` — accent hover
- `.text-success` / `.text-error` — semantic colors
- `.border-accent` / `.ring-accent` — accent for borders/rings
