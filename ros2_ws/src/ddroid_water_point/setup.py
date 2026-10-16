from setuptools import setup

package_name = "ddroid_water_point"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", ["launch/demo.launch.py"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="fabilous Lashidi",
    maintainer_email="n02528843x@students.nust.ac.zw",
    description="ROS 2 interface for the DDROID livestock water-point controller.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "ddroid_demo = ddroid_water_point.demo_node:main_demo",
            "ddroid_controller = ddroid_water_point.demo_node:main_controller",
        ],
    },
)
