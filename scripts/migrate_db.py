"""Database migration script to create/update tables"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.db.session import init_db, drop_db, engine
from app.db.models import Base


async def migrate():
    """Run database migration"""
    try:
        print("Starting database migration...")
        
        # Create all tables
        async with engine.begin() as conn:
            print("Creating/updating tables...")
            await conn.run_sync(Base.metadata.create_all)
        
        print("✓ Database migration completed successfully!")
        print("✓ All tables have been created/updated")
        
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        raise
    finally:
        await engine.dispose()


async def reset_db():
    """Reset database (drop and recreate all tables)"""
    try:
        print("WARNING: This will delete all data!")
        response = input("Are you sure you want to reset the database? (yes/no): ")
        
        if response.lower() != "yes":
            print("Reset cancelled")
            return
        
        print("Dropping all tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        
        print("Creating all tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("✓ Database has been reset successfully!")
        
    except Exception as e:
        print(f"✗ Reset failed: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "reset":
        asyncio.run(reset_db())
    else:
        asyncio.run(migrate())
