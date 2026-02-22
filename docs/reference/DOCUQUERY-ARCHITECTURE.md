# DocuQuery AI — Architecture

> Internal reference for Claude Code. Not visible in the app.

---

## Stack

| Layer       | Technology                          |
|-------------|-------------------------------------|
| Framework   | React 18.3 + TypeScript             |
| Build       | Vite                                |
| Styling     | Tailwind CSS + CSS custom properties |
| Routing     | react-router-dom v6                 |
| UI library  | shadcn/ui (Radix primitives)        |
| Icons       | Lucide React                        |
| Backend     | FastAPI on Render (external)        |
| Proxy       | Supabase Edge Function (CORS)      |

---

## Routing

Defined in `src/App.tsx`:

| Route   | Component  | Description                     |
|---------|------------|---------------------------------|
| `/`     | `Index`    | Main app (upload → chat)        |
| `/about`| `About`    | Static portfolio/project page   |
| `*`     | `NotFound` | 404 catch-all                   |

---

## State Management

**No global state** — the app is simple enough for local `useState` + `useCallback`.

### Index page state machine

```
upload → processing → chat
  ↑                     │
  └─────────────────────┘  (handleChange)
```

Key state in `Index`:
- `appState: "upload" | "processing" | "chat"` — drives which UI renders
- `fileInfo: FileInfo | null` — filename, type, chunk count after upload
- `messages: Message[]` — chat history (user + ai + error roles)
- `aiLoading: boolean` — shows skeleton loader
- `uploadError: string | null` — error in upload zone
- `steps: Step[]` — 3-step progress stepper status

---

## Theme System

- Toggle between dark (default) and light via `data-theme` attribute on `<html>`
- Persisted in `localStorage` key `"dq-theme"`
- Custom hook `useTheme()` in `Index.tsx`
- CSS variables swap in `index.css` (`:root` = dark, `html[data-theme="light"]` = light)
- **Does NOT use Tailwind's `darkMode: "class"`** for theming — uses CSS custom properties directly

---

## Backend Integration

### Direct calls (current)

The frontend calls the Render backend directly:

```
RENDER_BASE = "https://docuquery-ai-5rfb.onrender.com"
```

Two endpoints:
- `POST /upload` — multipart/form-data with `file` field
- `POST /query` — JSON `{ question: string }`

### CORS proxy (available but unused in current code)

A Supabase Edge Function at `supabase/functions/docuquery-proxy/index.ts` can proxy requests to avoid CORS issues. It forwards:
- `/docuquery-proxy/upload` → Render `/upload` (streams multipart body)
- `/docuquery-proxy/query` → Render `/query` (forwards JSON)

---

## API Contracts

### POST /upload

**Request:** `multipart/form-data` with `file` field (PDF, TXT, or CSV)

**Response (200):**
```json
{
  "filename": "report.pdf",
  "file_type": "pdf",
  "num_chunks": 42,
  "status": "ok"
}
```

**Error:** `{ "detail": "error message" }` with appropriate HTTP status.

### POST /query

**Request:**
```json
{ "question": "What is the main conclusion?" }
```

**Response (200):**
```json
{
  "answer": "The main conclusion is...",
  "sources": [
    {
      "chunk_index": 3,
      "page_start": 5,
      "page_end": 5,
      "row_start": null,
      "row_end": null,
      "distance": 0.23,
      "text_preview": "...relevant excerpt..."
    }
  ],
  "latency": 2.4
}
```

The frontend also accepts `response` or `result` as fallback keys for the answer text.

---

## File Structure

```
src/
├── App.tsx              # Router setup, providers (QueryClient, Tooltip, Toaster)
├── App.css              # Unused (styles in index.css)
├── index.css            # Design tokens, custom utilities, font imports
├── main.tsx             # React entry point
├── vite-env.d.ts        # Vite type declarations
│
├── pages/
│   ├── Index.tsx         # Main app — ALL custom components defined here
│   ├── About.tsx         # Static project/portfolio page
│   └── NotFound.tsx      # 404 page
│
├── components/
│   ├── NavLink.tsx       # react-router NavLink wrapper with active class support
│   └── ui/               # shadcn/ui components (accordion, button, card, etc.)
│
├── hooks/
│   ├── use-mobile.tsx    # Mobile breakpoint detection
│   └── use-toast.ts      # Toast hook
│
├── lib/
│   └── utils.ts          # cn() utility (clsx + tailwind-merge)
│
└── test/
    ├── setup.ts          # Vitest setup
    └── example.test.ts   # Example test

supabase/
└── functions/
    └── docuquery-proxy/
        └── index.ts      # CORS proxy edge function
```

---

## Code Conventions

1. **All custom components live in `Index.tsx`** — no separate files for Spinner, UploadZone, etc. This keeps the app self-contained since it's a single-page flow.

2. **Inline styles for theme colors** — components use `style={{ color: "hsl(var(--xxx))" }}` rather than Tailwind classes for dynamic theme values. Tailwind classes are used for layout and spacing.

3. **No CSS modules** — all styling is Tailwind utility classes + inline styles + custom utilities in `index.css`.

4. **Hover via JS** — `onMouseEnter`/`onMouseLeave` swap inline styles (no Tailwind `hover:` for theme-dependent colors).

5. **IDs via `uid()`** — simple `Math.random().toString(36).slice(2)` for message IDs.

6. **Error handling pattern** — try/catch with differentiated `TypeError` (network) vs `Error` (server) messages.

7. **Accepted file types** — constant `ACCEPTED = ".pdf,.txt,.csv"` used in file input.
