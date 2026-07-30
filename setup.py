"""
Setup para empaquetado de PulseDesk RAD.
"""

from setuptools import setup, find_packages

setup(
    name="pulsedesk",
    version="1.0.0",
    description="PulseDesk RAD - Centro de Control de Eventos en Tiempo Real",
    author="Tu Nombre",
    author_email="tu@email.com",
    packages=find_packages(),
    install_requires=[
        "customtkinter>=5.2.0",
    ],
    entry_points={
        "console_scripts": [
            "pulsedesk=main:main",
        ],
    },
    python_requires=">=3.11",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
    ],
)