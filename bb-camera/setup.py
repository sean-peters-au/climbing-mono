import setuptools

setuptools.setup(
    name="betaboard-camera",
    version="0.1.0",
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "flask",
        "picamera",
        "flask-cors",
    ],
)