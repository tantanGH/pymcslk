import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pymcslk",
    version="0.1.1",
    author="tantanGH",
    author_email="tantanGH@github",
    license='MIT',
    description="MCS file linker in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tantanGH/pymcslk",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'pymcslk=pymcslk.pymcslk:main'
        ]
    },
    packages=setuptools.find_packages(),
    python_requires=">=3.7",
    setup_requires=["setuptools"],
    install_requires=[],
)
