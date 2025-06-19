"""
EC 센서 패키지 설치 스크립트
"""

from setuptools import setup, find_packages

setup(
    name="taidacent-soil-sensor",
    version="0.1.0",
    description="Taidacent RS485 Soil NPK pH 센서를 위한 Python 라이브러리",
    author="JinYong An",
    author_email="jihk555@gmail.com",
    url="https://github.com/jihk321/ec-sensor",
    packages=find_packages(),
    install_requires=[
        "pyserial>=3.5",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries",
        "Topic :: System :: Hardware",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "ec-sensor=main:main",
        ],
    },
)
