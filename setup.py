from setuptools import setup, find_packages


def setup_package():
    setup(
        name="behavior collector",
        version="0.1.0",
        author="jungyoung",
        description="A package for behavior collector",
        packages=find_packages(),
        python_requires=">=3.10" ,
        install_requires=[
            "pyqt5",
            # "imutils",
            "opencv-python",
            "matplotlib"
        ],
        entry_points={
            "console_scripts": [
                "behav_collector = behavior_collector.__main__:main",
            ],
        },
    )

    
if __name__ == "__main__":
    setup_package()