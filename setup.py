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
        "flask-jwt-extended>=4.5.0",
        "werkzeug>=2.0.0",
        "python-dotenv>=1.0.0",
        "gunicorn>=21.2.0",
        
        # Security
        "pycryptodome>=3.18.0",
        "PyJWT>=2.8.0",
        "cryptography>=41.0.3",
        
        # Async support
        "gevent>=23.7.0",
        "greenlet>=2.0.2",
        
        # Utils and formatting
        "rich>=13.5.2",
        "python-decouple>=3.8",
        "certifi>=2023.7.22",
        "schedule>=1.2.0",
    ],
    extras_require={
        'dev': [
            "black>=23.7.0",
            "flake8>=6.1.0",
            "isort>=5.12.0",
            "pytest>=7.4.0",
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
