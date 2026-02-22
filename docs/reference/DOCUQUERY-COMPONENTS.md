# DocuQuery AI — Component Reference

> Internal reference for Claude Code. All custom components are defined in `src/pages/Index.tsx` unless noted.

---

## Index (main page)

**File:** `src/pages/Index.tsx` (default export)

### State

| State          | Type              | Description                          |
|----------------|-------------------|--------------------------------------|
| `appState`     | `AppState`        | `"upload" \| "processing" \| "chat"` |
| `fileInfo`     | `FileInfo \| null`| Filename, type, chunk count          |
| `messages`     | `Message[]`       | Chat history                         |
| `aiLoading`    | `boolean`         | Skeleton loader visible              |
| `uploadError`  | `string \| null`  | Error shown in upload zone           |
| `steps`        | `Step[]`          | 3-step progress stepper              |

### Refs

- `bottomRef` — scroll anchor at end of messages
- `aiAnchorRef` — latest AI message for scroll-into-view
- `scrollContainerRef` — chat scroll container for near-bottom detection

### Layout

```
┌─────────────────────────────────┐
│ Header (h-12)                   │
├─────────────────────────────────┤
│                                 │
│  upload:      UploadZone        │
│  processing:  ProgressStepper   │
│  chat:        ChatMessages      │
│                                 │
├─────────────────────────────────┤
│ chat: InputBar  /  else: Footer │
└─────────────────────────────────┘
```

---

## UploadZone

### Props

```ts
{
  onFile: (file: File) => void;
  uploadError: string | null;
}
```

### Behavior

- Drag-and-drop zone with dashed border
- Click opens native file picker (`accept=".pdf,.txt,.csv"`)
- Drag visual: border → accent, bg → accent/0.05
- Error banner appears below if `uploadError` is set (red, with X icon)
- Format badges: PDF, TXT, CSV shown as small bordered pills

### Dependencies

- Icons: `X` (error banner)

---

## ProgressStepper

### Props

```ts
{ steps: Step[] }

// where Step = { label: string; status: "pending" | "active" | "done" }
```

### Behavior

3 steps displayed vertically:
1. **done** → green circle with checkmark (success/0.15 bg)
2. **active** → spinning `Spinner` (accent color)
3. **pending** → empty circle with border

Steps are animated sequentially during upload: pending → active → done.

### Dependencies

- `Spinner`, `Check` icon

---

## ChatMessages

### Props

```ts
{
  messages: Message[];
  loading: boolean;
  bottomRef: React.RefObject<HTMLDivElement>;
  aiAnchorRef: React.RefObject<HTMLDivElement>;
  scrollContainerRef: React.RefObject<HTMLDivElement>;
  onSuggest: (s: string) => void;
}
```

### Behavior

- **Empty state**: "Ask anything about your document" + 3 suggestion chips
- **Messages**: User bubbles (right, accent bg) + AI bubbles (left, surface bg) + error bubbles (left, error color)
- **AI indicator**: small accent dot (1.5×1.5) before AI/error messages
- **Loading**: `SkeletonLoader` shown when `loading=true`
- **Auto-scroll**: scrolls to latest AI message via `aiAnchorRef`

### Suggestion chips

Hardcoded in `SUGGESTIONS` constant:
- "What is this document about?"
- "Summarize the key points"
- "What are the main conclusions?"

### Dependencies

- `AiBubble`, `SkeletonLoader`

---

## AiBubble

### Props

```ts
{ msg: Message }
```

### Behavior

- Surface-colored rounded box with border
- **Copy button**: appears on hover (top-right), copies `msg.content` to clipboard
- **Markdown**: renders content via `MarkdownContent`
- **Sources**: renders `SourceCards` if sources present
- **Latency**: shows "Generated in X.Xs" with Zap icon if latency available

### Dependencies

- `MarkdownContent`, `SourceCards`
- Icons: `Copy`, `Check`, `Zap`

---

## SourceCards

### Props

```ts
{ sources: Source[] }

// Source = {
//   chunk_index: number;
//   page_start: number | null;
//   page_end: number | null;
//   row_start: number | null;
//   row_end: number | null;
//   distance: number;
//   text_preview: string;
// }
```

### Behavior

- Horizontal flex-wrap of citation cards
- Each card shows: FileText icon + label (Page X–Y / Rows X–Y / Chunk N)
- **Collapsed**: 2-line preview, chevron down
- **Expanded**: full preview + score badge (e.g. "78% match"), chevron up, accent border
- Toggle via click, multiple can be expanded simultaneously (Set-based state)

### Label logic

1. If `page_start` is set → "Page X–Y"
2. Else if `row_start` is set → "Rows X–Y"
3. Else → "Chunk N"

### Score calculation

```ts
score = Math.round((1 - source.distance) * 100)
```

### Dependencies

- Icons: `FileText`, `ChevronDown`, `ChevronUp`

---

## InputBar

### Props

```ts
{
  onSend: (q: string) => void;
  loading: boolean;
}
```

### Behavior

- Auto-resizing textarea (min 40px, max 160px)
- **Enter** sends (Shift+Enter for newline)
- Send button: accent bg, disabled when empty or loading
- Loading state: button shows `Spinner` instead of `ArrowUp`
- Auto-focuses on mount

### Dependencies

- `Spinner`
- Icons: `ArrowUp`

---

## MarkdownContent

### Props

```ts
{ text: string }
```

### Behavior

Lightweight markdown renderer (no library):
- Splits on double newline → paragraphs
- Detects lines starting with `- ` or `* ` → `<ul>` with `<li>`
- `**bold**` → `<strong>`
- Single newlines → `<br />`

---

## SkeletonLoader

No props.

### Behavior

3 bouncing dots (2×2px circles in muted-foreground) with staggered animation:
- Delays: 0ms, 160ms, 320ms
- Duration: 1.2s each
- Uses Tailwind `animate-bounce`

---

## Spinner

### Props

```ts
{ size?: number; className?: string }
```

Default `size=16`. Inline SVG with `animate-spin`:
- Faded circle (strokeOpacity 0.25)
- Quarter-arc in full opacity
- Inherits `currentColor`

---

## About

**File:** `src/pages/About.tsx` (default export)

### Structure

Static page, no state. Sections:

1. **Hero** — Title + subtitle
2. **The Problem** — Text paragraph
3. **Key Decisions** — 3-column grid table (Decision / What I Chose / Why)
4. **Evaluation Results** — 2×2 grid of metric cards (87.5% accuracy, 0% hallucination, 75% citations, 8.5s latency)
5. **What I'd Improve** — 3 items with accent left-border
6. **Tech Stack** — Pill badges (Python, FastAPI, React, TypeScript, Claude Sonnet, OpenAI Embeddings, NumPy, Tailwind CSS)
7. **Built by** — Author info + GitHub/LinkedIn links

### Dependencies

- Icons: `ArrowLeft`
- `Link` from react-router-dom

---

## NavLink

**File:** `src/components/NavLink.tsx`

### Props

```ts
{
  className?: string;
  activeClassName?: string;
  pendingClassName?: string;
  to: string;
  // ...rest of NavLinkProps
}
```

Wrapper around react-router-dom's `NavLink` that supports separate `activeClassName` and `pendingClassName` strings (merged via `cn()`).

---

## NotFound

**File:** `src/pages/NotFound.tsx` (default export)

### Behavior

- Logs 404 error to console with attempted path
- Displays "404 / Oops! Page not found" with link to home
- Centered layout on muted background

---

## Type Definitions

All defined at the top of `Index.tsx`:

```ts
type AppState = "upload" | "processing" | "chat";
type StepStatus = "pending" | "active" | "done";
type MessageRole = "user" | "ai" | "error";

interface Source {
  chunk_index: number;
  page_start: number | null;
  page_end: number | null;
  row_start: number | null;
  row_end: number | null;
  distance: number;
  text_preview: string;
}

interface Message {
  id: string;
  role: MessageRole;
  content: string;
  sources?: Source[];
  latency?: number;
  ts: Date;
}

interface FileInfo {
  filename: string;
  file_type: string;
  num_chunks: number;
}

interface Step {
  label: string;
  status: StepStatus;
}
```

---

## Helper Functions

| Function     | Description                                     |
|--------------|-------------------------------------------------|
| `uid()`      | Random ID: `Math.random().toString(36).slice(2)` |
| `useTheme()` | Dark/light toggle hook with localStorage         |
| `renderInline(text)` | Parses `**bold**` in text                |
