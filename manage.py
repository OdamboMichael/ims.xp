#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys
import platform
from pathlib import Path
from datetime import datetime

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ims.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Custom command-line enhancements
    if len(sys.argv) > 1:
        handle_custom_commands(sys.argv)
    
    execute_from_command_line(sys.argv)

def handle_custom_commands(argv):
    """Handle custom command-line arguments and enhancements."""
    command = argv[1]
    
    if command == 'runserver':
        # Display custom startup message
        display_startup_message()
        
        # Check for environment file
        check_environment_file()
        
        # Check database connection
        check_database_connection()
        
        # Ensure media directories exist
        ensure_directories()
        
    elif command == 'migrate':
        print("🚀 Running migrations for Xpert Farmer IMS...")
        
    elif command == 'createsuperuser':
        print("👑 Creating superuser for Xpert Farmer IMS...")
        
    elif command == 'collectstatic':
        print("📦 Collecting static files for Xpert Farmer IMS...")
        
    elif command == 'shell':
        print("🐍 Starting Django shell for Xpert Farmer IMS...")
        
    elif command == 'test':
        print("🧪 Running tests for Xpert Farmer IMS...")

def display_startup_message():
    """Display custom startup message."""
    print("\n" + "="*60)
    print("🚜 Xpert Farmer IMS - Farm Management System")
    print("="*60)
    
    # System information
    print(f"\n📊 System Information:")
    print(f"   • Python: {platform.python_version()}")
    print(f"   • Django: (will be shown after import)")
    print(f"   • Platform: {platform.system()} {platform.release()}")
    print(f"   • Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Environment information
    env = os.environ.get('DJANGO_SETTINGS_MODULE', 'Not set')
    debug = os.environ.get('DEBUG', 'Not set')
    print(f"\n⚙️  Environment:")
    print(f"   • Settings: {env}")
    print(f"   • Debug Mode: {debug}")
    
    # Project structure
    print(f"\n📁 Project Structure:")
    print(f"   • Project Root: {PROJECT_ROOT}")
    print(f"   • Static Files: {PROJECT_ROOT / 'static'}")
    print(f"   • Media Files: {PROJECT_ROOT / 'media'}")
    print(f"   • Templates: {PROJECT_ROOT / 'ims' / 'templates'}")
    
    print("\n" + "="*60)
    print("Starting development server...")
    print("="*60 + "\n")

def check_environment_file():
    """Check if .env file exists and load it."""
    env_file = PROJECT_ROOT / '.env'
    
    if env_file.exists():
        print(f"✅ Found environment file: {env_file}")
        
        # Try to load environment variables from .env
        try:
            from decouple import config, AutoConfig
            config = AutoConfig(search_path=PROJECT_ROOT)
            print(f"   • Database: {config('DATABASE_URL', default='Not configured').split('@')[1] if '@' in config('DATABASE_URL', default='') else 'Local database'}")
            print(f"   • Secret Key: {'Set' if config('SECRET_KEY', default='') else 'Not set'}")
            print(f"   • Allowed Hosts: {config('ALLOWED_HOSTS', default='localhost,127.0.0.1')}")
        except ImportError:
            print("   ⚠️  python-decouple not installed, .env file won't be loaded")
        except Exception as e:
            print(f"   ⚠️  Error loading .env file: {e}")
    else:
        print("⚠️  No .env file found. Using default settings.")
        print("   Consider creating a .env file for production settings.")

def check_database_connection():
    """Check database connection before starting server."""
    try:
        import django
        django.setup()
        
        from django.db import connection
        from django.db.utils import OperationalError
        
        # Try to connect to database
        connection.ensure_connection()
        db_info = connection.get_connection_params()
        
        print(f"✅ Database connection successful:")
        print(f"   • Engine: {connection.vendor}")
        print(f"   • Name: {db_info.get('database', 'Unknown')}")
        print(f"   • Host: {db_info.get('host', 'localhost')}")
        print(f"   • Port: {db_info.get('port', 'default')}")
        
        # Check if migrations are applied
        from django.core.management import execute_from_command_line
        from django.db.migrations.executor import MigrationExecutor
        
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        
        if plan:
            print("⚠️  There are unapplied migrations:")
            for migration, _ in plan:
                print(f"   • {migration.app_label}.{migration.name}")
            print("   Run 'python manage.py migrate' to apply them.")
        else:
            print("✅ All migrations are applied.")
            
    except OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        print("   Please check your database configuration in .env file.")
        print("   Defaulting to SQLite for development.")
    except Exception as e:
        print(f"⚠️  Could not check database: {e}")

def ensure_directories():
    """Ensure required directories exist."""
    directories = [
        PROJECT_ROOT / 'media',
        PROJECT_ROOT / 'media/profiles',
        PROJECT_ROOT / 'media/farms',
        PROJECT_ROOT / 'media/documents',
        PROJECT_ROOT / 'staticfiles',
        PROJECT_ROOT / 'logs'
    ]
    
    for directory in directories:
        try:
            directory.mkdir(parents=True, exist_ok=True)
            # print(f"✅ Directory ensured: {directory}")
        except Exception as e:
            print(f"⚠️  Could not create directory {directory}: {e}")

def create_default_admin():
    """Create default admin user if none exists."""
    try:
        import django
        django.setup()
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@xpertfarmer.com',
                password='admin123'
            )
            print("✅ Created default admin user: admin / admin123")
            print("⚠️  Change this password immediately in production!")
    except Exception as e:
        print(f"⚠️  Could not create default admin: {e}")

if __name__ == '__main__':
    # Add custom command-line argument parsing
    if '--create-admin' in sys.argv:
        create_default_admin()
        sys.argv.remove('--create-admin')
    
    # Add help flag
    if '--help' in sys.argv or '-h' in sys.argv:
        print("\nXpert Farmer IMS - Management Commands")
        print("="*50)
        print("\nStandard Django commands:")
        print("  runserver      Start development server")
        print("  migrate        Apply database migrations")
        print("  makemigrations Create new migrations")
        print("  createsuperuser Create admin user")
        print("  collectstatic  Collect static files")
        print("  shell          Start Django shell")
        print("  test           Run tests")
        
        print("\nCustom options:")
        print("  --create-admin Create default admin user (admin/admin123)")
        print("  --check-env    Check environment configuration")
        print("  --version      Show version information")
        print("\nExamples:")
        print("  python manage.py runserver --settings=ims.settings")
        print("  python manage.py migrate")
        print("  python manage.py createsuperuser")
        print("  python manage.py --create-admin")
        
        if '--help' in sys.argv:
            sys.argv.remove('--help')
        if '-h' in sys.argv:
            sys.argv.remove('-h')
    
    # Add version flag
    if '--version' in sys.argv or '-v' in sys.argv:
        try:
            import django
            print(f"\nXpert Farmer IMS")
            print(f"Django {django.get_version()}")
            print(f"Python {platform.python_version()}")
        except:
            pass
        
        if '--version' in sys.argv:
            sys.argv.remove('--version')
        if '-v' in sys.argv:
            sys.argv.remove('-v')
    
    # Add environment check flag
    if '--check-env' in sys.argv:
        check_environment_file()
        sys.argv.remove('--check-env')
    
    main()