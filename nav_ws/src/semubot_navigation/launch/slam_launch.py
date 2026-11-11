import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

WHEELBASE_PKG = 'semubot_bringup'
WHEELBASE_LAUNCH = 'ros2ctrl_microros.launch.py'


def generate_launch_description():
    nav = get_package_share_directory('semubot_navigation')
    sllidar = get_package_share_directory('sllidar_ros2')
    slam = get_package_share_directory('slam_toolbox')
    wheelbase = get_package_share_directory(WHEELBASE_PKG)

    return LaunchDescription([
        # 1. Wheelbase stack
        IncludeLaunchDescription(PythonLaunchDescriptionSource(
            os.path.join(wheelbase, 'launch', WHEELBASE_LAUNCH))),

        # 2. odom -> base_link transform from /odom
        Node(package='odom_to_tf_ros2', executable='odom_to_tf',
             parameters=[{'odom_topic': '/odom'}], output='screen'),

        # 3. Temporary base_link -> laser (adjust x/y/z to the real mounting position)
        Node(package='tf2_ros', executable='static_transform_publisher',
             arguments=['--x', '-0.2', '--y', '0', '--z', '0.3',
                        '--frame-id', 'base_link', '--child-frame-id', 'laser']),

        # 4. Lidar
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(sllidar, 'launch', 'sllidar_a3_launch.py')),
            launch_arguments={'serial_baudrate': '256000',
                              'frame_id': 'laser'}.items()),

        # 5. SLAM
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(slam, 'launch', 'online_async_launch.py')),
            launch_arguments={'slam_params_file':
                              os.path.join(nav, 'config', 'slam_params.yaml')}.items()),
    ])