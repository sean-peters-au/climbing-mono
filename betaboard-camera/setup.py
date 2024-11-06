import setuptools

setuptools.setup(
    name="betaboard_camera",
    version="0.1.0",
    package_dir={"": "src"},
    packages=setuptools.find_namespace_packages(where="src"),
    python_requires=">=3.9",
    install_requires=[
        "flask>=2.0.0",
        "flask-cors>=3.0.0",
    ],
)