# Deployment Guide - STAE Sistema de Acesso

## Infrastructure
- **Database**: Supabase (PostgreSQL)
- **Web Server**: Render

## Setup Instructions

### 1. Supabase Setup
1. Create a Supabase project at https://supabase.com
2. Go to SQL Editor and run the schema from `supabase_schema.sql`
3. Get your DATABASE_URL from Supabase Settings > Database
4. (Optional) Set up Supabase Auth if using Supabase client

### 2. Render Deployment
1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set the following environment variables:
   - `DATABASE_URL`: Your Supabase connection string
   - `STAE_SECRET_KEY`: Generate a secure random key
   - `STAE_DEBUG`: `false`
   - `STAE_HOST`: `0.0.0.0`
   - `STAE_PORT`: `5000`
4. Deploy

### 3. Local Development with Supabase
Set the `DATABASE_URL` environment variable to use Supabase locally:
```bash
export DATABASE_URL=postgresql://postgres:password@db.supabase.co:5432/postgres
python run.py
```

### 4. Local Development with SQLite
To use SQLite locally, don't set `DATABASE_URL`:
```bash
python run.py
```

## Permission System

### Role Permissions
- **Admin**: Full access including dashboard, operator management, logs, backups
- **Supervisor**: Full access except can't delete Admin accounts
- **RH**: Can register employees and interns, change own password
- **Policia**: Can register all visitor types, register exits, generate receipts

### Registration Types by Role
- **Policia**: Funcionario, Estagiario, Visitante
- **RH**: Funcionario, Estagiario
- **Admin/Supervisor**: Funcionario, Estagiario, Visitante

## Default Accounts
After first run, these accounts are created:
- Admin: `admin` / `admin123`
- Policia: `policia` / `policia123`
- RH: `rh` / `rh123`
- Supervisor: `supervisor` / `stae2026`

**Important**: Change default passwords in production!
