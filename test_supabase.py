#!/usr/bin/env python
"""
Test script to verify Supabase connection and basic operations.
Run this after setting DATABASE_URL environment variable.
"""

import os
import sys

# Set DATABASE_URL for testing (replace with your actual URL)
os.environ["DATABASE_URL"] = "postgresql://postgres:Cessy.Maker1@db.inszsbbflhizvvqrxmpm.supabase.co:6543/postgres"

try:
    from app.backend import BACKEND, get_db
    print("[OK] Backend module loaded successfully")
except Exception as e:
    print(f"[ERROR] Error loading backend: {e}")
    sys.exit(1)

print(f"[OK] Backend kind: {BACKEND.kind}")

try:
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT version()")
            version = cursor.fetchone()
            print(f"[OK] Database version: {version['version'][:50]}...")
            
            cursor.execute("SELECT COUNT(*) as count FROM operadores")
            count = cursor.fetchone()
            print(f"[OK] Operadores count: {count['count']}")
            
            cursor.execute("SELECT COUNT(*) as count FROM registos_acesso")
            count = cursor.fetchone()
            print(f"[OK] Registos count: {count['count']}")
            
            # Check existing schema
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'registos_acesso'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            print(f"\n[INFO] Existing 'registos_acesso' columns:")
            for col in columns:
                print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
            
    print("\n[SUCCESS] All tests passed! Supabase connection is working.")
except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
