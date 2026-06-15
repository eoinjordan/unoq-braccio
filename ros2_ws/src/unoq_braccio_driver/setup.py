from setuptools import setup

package_name = "unoq_braccio_driver"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
    ],
    install_requires=["setuptools", "pyserial", "PyYAML"],
    zip_safe=True,
    maintainer="Eoin Jordan",
    maintainer_email="eoin@example.com",
    description="USB serial, TCP, and pose helpers for UNO Q Braccio.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "serial_bridge = unoq_braccio_driver.serial_bridge:main",
            "tcp_bridge = unoq_braccio_driver.tcp_bridge:main",
            "pose_demo = unoq_braccio_driver.pose_demo:main",
            "edge_impulse_mapper = unoq_braccio_driver.edge_impulse_mapper:main",
            "joint_state_simulator = unoq_braccio_driver.joint_state_simulator:main",
        ],
    },
)
