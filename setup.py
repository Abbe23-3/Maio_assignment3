from setuptools import setup, find_packages

setup(
    name="diabetes-triage",
    version="0.2.0",
    description="Virtual Diabetes Clinic Triage ML Service",
    author="MLOps Team 5",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "scikit-learn>=1.3.2",
        "pandas>=2.1.4",
        "numpy>=1.24.4",
        "pydantic>=2.5.0",
        "joblib>=1.3.2",
        "pyyaml>=6.0.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "httpx>=0.25.2",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
        ]
    },
    entry_points={
        "console_scripts": [
            "diabetes-train=diabetes_triage.training.train:main",
            "diabetes-api=diabetes_triage.api.main:main",
        ],
    },
)
