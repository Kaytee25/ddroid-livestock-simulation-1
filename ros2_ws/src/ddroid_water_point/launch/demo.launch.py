from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch.substitutions import FindExecutable


def generate_launch_description():
    return LaunchDescription(
        [
            ExecuteProcess(
                cmd=[
                    FindExecutable(name="ddroid_demo"),
                    "--gazebo",
                ],
                output="screen",
            )
        ]
    )
