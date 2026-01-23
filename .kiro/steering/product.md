# Product Overview

QYD (QYD项目管理系统) is a full-stack project management system for managing users, projects, servers, and email accounts with enterprise-grade features.

## Core Features

- **User Management**: User CRUD, role-based access control (RBAC), JWT authentication, API token management, operation logging
- **Project Management**: Project info, accounts, wallets, balance tracking with batch operations
- **Server Management**: Server info, country/region management, grouping, account management
- **Mail Management**: Email info management, Outlook integration, HTML mail viewer with search and caching
- **Enterprise Features**: RBAC permissions, Redis queue processing, MySQL read-write splitting, intelligent caching, automated log rotation

## User Roles

- **ADMIN**: Full system access
- **GM**: Project manager permissions
- **IT**: Technical staff permissions  
- **MANUAL**: Manual operator (default role)

## Default Admin Account

- Email: `zhiyu`
- Password: `2201101122@qq.com`
- Role: ADMIN

## Key Characteristics

- Bilingual codebase (Chinese documentation, mixed Chinese/English code)
- Async-first architecture (FastAPI backend, React frontend)
- Enterprise-grade: supports high concurrency, batch processing, read-write splitting
- RESTful API with auto-generated documentation (Swagger/ReDoc)
