# LavenderSentinel Frontend

React + TypeScript frontend for LavenderSentinel.

## Development Setup

### Prerequisites

- Node.js 20+ (recommend using [nvm](https://github.com/nvm-sh/nvm) or [fnm](https://github.com/Schniz/fnm))
- npm 10+ or pnpm

### Install Dependencies

```bash
cd frontend

# Clean install (recommended if having issues)
rm -rf node_modules package-lock.json
npm install

# Or just install
npm install
```

### Run Development Server

```bash
npm run dev
```

The app will be available at http://localhost:5173

### Build for Production

```bash
npm run build
npm run preview  # Preview the production build
```

## Common Issues

### Clear Cache & Reinstall

If you encounter dependency issues:

```bash
# Remove all cached files
rm -rf node_modules
rm -rf .vite
rm -f package-lock.json

# Clear npm cache
npm cache clean --force

# Reinstall
npm install
```

### Using pnpm (Alternative)

```bash
# Install pnpm
npm install -g pnpm

# Install dependencies
pnpm install

# Run dev server
pnpm dev
```

## Project Structure

```
frontend/
├── src/
│   ├── components/     # React components
│   │   ├── ui/         # Base UI components
│   │   ├── layout/     # Layout components
│   │   ├── paper/      # Paper-related components
│   │   └── chat/       # Chat components
│   ├── pages/          # Page components
│   ├── services/       # API services
│   ├── stores/         # Zustand stores
│   ├── hooks/          # Custom React hooks
│   ├── types/          # TypeScript types
│   ├── lib/            # Utility functions
│   ├── App.tsx         # Root component
│   └── main.tsx        # Entry point
├── public/             # Static assets
├── index.html          # HTML template
├── package.json        # Dependencies
├── vite.config.ts      # Vite configuration
├── tailwind.config.js  # Tailwind CSS config
└── tsconfig.json       # TypeScript config
```

## Available Scripts

| Script | Description |
|--------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build |
| `npm run lint` | Run ESLint |
| `npm run type-check` | Run TypeScript type checking |

## Environment Variables

Create a `.env` file (optional):

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

In development, the Vite proxy handles API requests automatically.

