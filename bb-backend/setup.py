import setuptools

setuptools.setup(
    name="betaboard",
    version="0.1.0",
    package_dir={"": "src"},
    packages=setuptools.find_namespace_packages(where="src"),
    python_requires=">=3.9",
    install_requires=[
        "sqlalchemy>=2.0.0",
        "alembic>=1.12.0",
        "psycopg2-binary>=2.9.0",
        "flask>=2.0.0",
    ],
)