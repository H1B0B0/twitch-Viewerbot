from setuptools import setup, find_packages

setup(
    name="TwitchViewerBOT",
    version="2.3",
    description="Twitch Bot for making fake viewers on your live",
    packages=find_packages(where="backend"),
    package_dir={"": "backend"},
    python_requires=">=3.9",
    install_requires=[
        # Base dependencies
        "requests[socks]>=2.28.0",
        "streamlink>=5.5.1",
        "fake_useragent>=1.1.1",
        "websocket-client>=1.6.1",
        
        # Flask and related
        "flask>=2.0.0",
        "flask-cors>=4.0.0",
        "flask-sqlalchemy>=3.0.0",
        "flask-login>=0.6.0",
        "flask-jwt-extended>=4.5.0",
        "flask-migrate>=4.0.4",
        "werkzeug>=2.0.0",
        "python-dotenv>=1.0.0",
        "gunicorn>=21.2.0",
        
        # Database
        "SQLAlchemy>=2.0.0",
        "alembic>=1.0.0",
        "psycopg2-binary>=2.9.7",
        "redis>=4.6.0",
        
        # UI and formatting
        "rich>=13.5.2",
        "customtkinter>=5.2.0",
        "emoji>=2.8.0",
        "colorama>=0.4.6",
        
        # Security and encryption
        "pycryptodome>=3.18.0",
        "cffi>=1.15.1",
        "bcrypt>=4.0.1",
        "PyJWT>=2.8.0",
        "cryptography>=41.0.3",
        
        # Async support
        "aiohttp>=3.8.5",
        "asgiref>=3.7.2",
        "asyncio>=3.4.3",
        "gevent>=23.7.0",
        "greenlet>=2.0.2",
        
        # ML/AI dependencies
        "torch>=2.0.1",
        "numpy>=1.24.3",
        "openai>=0.27.8",
        "transformers>=4.31.0",
        "faster-whisper>=0.7.1",
        
        # Discord Integration
        "discord.py>=2.3.2",
        "discord-webhook>=1.1.0",
        
        # Network and Proxy
        "PySocks>=1.7.1",
        "selenium>=4.11.2",
        "urllib3>=2.0.4",
        "beautifulsoup4>=4.12.2",
        "cloudscraper>=1.2.71",
        
        # Utilities
        "python-decouple>=3.8",
        "argparse>=1.4.0",
        "python-dateutil>=2.8.2",
        "pytz>=2023.3",
        "tqdm>=4.65.0",
        "certifi>=2023.7.22",
        "pyOpenSSL>=23.2.0",
        "certbot>=2.6.0",
        "schedule>=1.2.0",
        "six>=1.16.0",
        "cachetools>=5.3.1"
    ],
    extras_require={
        'test': [
            "pytest>=7.4.0",
            "pytest-flask>=1.2.0",
            "pytest-asyncio>=0.21.1",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.1",
            "coverage>=7.3.0",
            "faker>=19.3.0"
        ],
        'dev': [
            "black>=23.7.0",
            "flake8>=6.1.0",
            "isort>=5.12.0",
            "mypy>=1.5.1",
            "pre-commit>=3.3.3",
            "pylint>=2.17.5",
            "autopep8>=2.0.2",
            "rope>=1.9.0",
            "bandit>=1.7.5"
        ]
    },
    entry_points={
        'console_scripts': [
            'twitchbot=backend.main:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
