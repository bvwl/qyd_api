# Project Structure

## Root Organization

```
qyd_api2/
├── backend/          # FastAPI backend service
├── frontend/         # React frontend application
├── docs/             # Project documentation
├── scripts/          # Project-level utility scripts
└── logs/             # Application logs
```

## Backend Structure (`backend/`)

```
backend/
├── app/
│   ├── apis/              # API routes
│   │   ├── deps.py        # Dependency injection (JWT auth, permissions)
│   │   └── v1/            # API v1 endpoints
│   │       ├── user/      # User management APIs
│   │       ├── project/   # Project management APIs
│   │       ├── server/    # Server management APIs
│   │       └── mail/      # Mail management APIs
│   ├── core/              # Core configuration
│   │   ├── settings.py    # App settings and config
│   │   ├── database.py    # Database config (read-write splitting)
│   │   ├── tools.py       # Utility functions (password hashing, etc.)
│   │   └── verify.py      # Validation functions
│   ├── crud/              # Database operations layer (organized by domain)
│   ├── models/            # Tortoise ORM models
│   │   ├── base.py        # Base model with common fields
│   │   ├── user.py        # User, Role, Route, Token, Log models
│   │   ├── project.py     # Project, Account, Wallet models
│   │   ├── server.py      # Server, Country, Group, Account models
│   │   └── mail.py        # Mail models
│   ├── schemas/           # Pydantic models (request/response)
│   ├── utils/             # Utility modules
│   │   ├── jwt_tool.py    # JWT token generation/verification
│   │   ├── time_tool.py   # Time parsing and formatting
│   │   ├── logs.py        # Logging utilities
│   │   ├── redis_queue.py # Redis queue base class
│   │   ├── project_account_queue.py  # Project account queue
│   │   ├── data_permission.py        # Data permission filtering
│   │   ├── decorators.py  # Custom decorators
│   │   ├── exceptions.py  # Custom exceptions
│   │   └── log_middleware.py  # Request logging middleware
│   ├── clients/           # External API clients (Outlook, etc.)
│   ├── logs/              # Logging configuration
│   ├── tests/             # Test files
│   └── main.py            # Application entry point
├── db/                    # Database initialization scripts
│   ├── init_roles_and_admin.py  # Initialize roles and admin user
│   ├── init_routes.py     # Initialize route permissions
│   └── *.sql              # SQL migration scripts
├── migrations/            # Aerich database migrations
├── scripts/               # Backend utility scripts
├── logs/                  # Log files (auto-rotated)
├── .env                   # Environment variables
├── requirements.txt       # Python dependencies
└── start.py              # Server startup script
```

## Frontend Structure (`frontend/`)

```
frontend/
├── src/
│   ├── api/              # API client layer
│   │   ├── index.ts      # Axios config, interceptors
│   │   ├── user.ts       # User API calls
│   │   ├── project.ts    # Project API calls
│   │   ├── server.ts     # Server API calls
│   │   └── mail.ts       # Mail API calls
│   ├── components/       # Reusable components
│   │   ├── Layout/       # Main layout with sidebar/header
│   │   ├── ProtectedRoute/  # Route authentication guard
│   │   ├── Permission/   # Permission-based rendering
│   │   └── ApiTester/    # API testing tool
│   ├── views/            # Page components (organized by feature)
│   │   ├── Login/        # Login page
│   │   ├── Dashboard/    # Dashboard with stats
│   │   ├── User/         # User management pages
│   │   ├── Project/      # Project management pages
│   │   ├── Server/       # Server management pages
│   │   ├── Mail/         # Mail management pages
│   │   └── ApiDocs/      # API documentation/testing pages
│   ├── store/            # Zustand state management
│   │   └── useUserStore.ts  # User state (auth, permissions)
│   ├── hooks/            # Custom React hooks
│   │   └── usePermission.ts  # Permission checking hook
│   ├── utils/            # Utility functions
│   │   ├── token.ts      # Token management
│   │   ├── format.ts     # Data formatting
│   │   └── constants.ts  # App constants
│   ├── types/            # TypeScript type definitions
│   │   └── index.ts      # Shared types
│   ├── router/           # Route configuration
│   ├── App.tsx           # Root component
│   └── main.tsx          # Application entry
├── tests/                # Test files and utilities
├── public/               # Static assets
├── .env.development      # Development environment config
├── .env.production       # Production environment config
├── vite.config.ts        # Vite configuration
├── tsconfig.json         # TypeScript configuration
└── package.json          # Dependencies and scripts
```

## Documentation Structure (`docs/`)

```
docs/
├── guides/       # Usage guides (RBAC, Redis, permissions, etc.)
├── summaries/    # Feature implementation summaries
├── api/          # API documentation
├── features/     # Feature documentation
└── fixes/        # Bug fixes and update records
```

## Scripts Structure (`scripts/`)

```
scripts/
├── mysql/        # MySQL deployment and management scripts
├── test/         # Testing scripts (API, permissions, etc.)
├── debug/        # Debugging utilities
└── utils/        # General utility scripts
```

## Key Architectural Patterns

### Backend

- **Layered Architecture**: APIs → CRUD → Models
- **Dependency Injection**: `deps.py` provides reusable auth dependencies
- **Read-Write Splitting**: `database.py` provides `db_read()` and `db_write()` helpers
- **Async-First**: All I/O operations are async
- **Exception Handling**: Centralized in `app/core/__init__.py`

### Frontend

- **Feature-Based Organization**: Views organized by domain (User, Project, Server, Mail)
- **API Layer Separation**: All API calls in `src/api/`
- **Global State**: Zustand for user auth and permissions
- **Route Protection**: `ProtectedRoute` component wraps authenticated routes
- **Permission-Based Rendering**: `usePermission` hook for conditional UI

## Naming Conventions

- **Backend**: snake_case for Python (files, functions, variables)
- **Frontend**: camelCase for TypeScript/React (variables, functions), PascalCase for components
- **Database**: snake_case for table and column names
- **API Routes**: `/api/v1/{domain}/{action}` pattern
- **Files**: Descriptive names matching their primary export/purpose
