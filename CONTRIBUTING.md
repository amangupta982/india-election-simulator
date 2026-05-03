# Contributing to India Election Simulator

Thank you for contributing to this civic education project! 🏛️

## Development Setup

### Backend (Python 3.12+)
```bash
cd india-democracy-simulator/backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend (Node.js 20+)
```bash
cd india-democracy-simulator/frontend
npm install
cp .env.example .env.local  # Add your Firebase credentials
npm run dev
```

## Testing

### Backend Tests (pytest)
```bash
cd india-democracy-simulator/backend
pytest -v --cov=app --cov-report=term
```

### Frontend Tests (Jest)
```bash
cd india-democracy-simulator/frontend
npx jest --ci
```

## Code Quality Standards

- **Python**: Follow PEP 8, use type hints on all function signatures
- **TypeScript**: Strict mode enabled, no `any` types in production code
- **Docstrings**: All public functions must have Google-style docstrings
- **Tests**: New features require corresponding test coverage (target: 90%+)
- **Linting**: `eslint` must pass with zero errors before PR merge
- **Security**: Never commit API keys or secrets — use `.env.local` files

## Architecture

```
india-democracy-simulator/
├── backend/              # FastAPI + SQLAlchemy
│   ├── app/
│   │   ├── models.py     # SQLAlchemy ORM models
│   │   ├── config.py     # Pydantic Settings
│   │   ├── routers/      # API route handlers
│   │   └── services/     # Business logic (game engine, AI, seat math)
│   └── tests/            # pytest async test suite
├── frontend/             # Next.js 16 + React 19
│   ├── app/              # App Router pages
│   ├── components/       # Reusable UI components
│   ├── store/            # Zustand state management
│   ├── lib/              # API client, Firebase config
│   └── __tests__/        # Jest test suite
└── deploy.sh             # Cloud Run deployment script
```

## Commit Convention

Use [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` New features
- `fix:` Bug fixes
- `test:` Adding/updating tests
- `docs:` Documentation changes
- `refactor:` Code restructuring
- `ci:` CI/CD pipeline changes

## License

MIT — See [LICENSE](LICENSE) for details.
