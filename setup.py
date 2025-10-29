"""Setup configuration for Game of Life."""
from setuptools import find_packages, setup

setup(
    name="gamelife",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    install_requires=[
        "matplotlib>=3.8.0",
        "platformdirs>=4.0.0",
    ],
    extras_require={
        "gui": [
            "ttkbootstrap>=1.10.1; platform_system != 'Darwin'",
            "pillow>=10.0.0",
        ],
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.9.0",
            "isort>=5.12.0",
            "pylint>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "gamelife=gamelife.__main__:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A gamified task manager application",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    keywords="task-manager, gamification, productivity",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Time Tracking",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.12",
    ],
)