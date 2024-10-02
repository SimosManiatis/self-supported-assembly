import robolink as rl    # RoboDK API for controlling and communicating with RoboDK
import robodk as rdk     # RoboDK tools, such as matrix operations and other utilities
import Rhino.Geometry as rg
import math

# === Inputs ===
# RobotName: Name of the robot in RoboDK (e.g., "UR5")
# UpdateRoboDK: Boolean toggle to execute the script and update RoboDK when True
# TargetPoint0: The starting point where the robot should move first (Rhino Point3d)
# TargetPointA: The final point where the robot should move and end the program (Rhino Point3d)
# BaseRotationZ: Rotation of the robot's base around the Z-axis in degrees (optional, can be 0 if no rotation is needed)

# Initialize outputs
SuccessMessage = ""
TargetPose0 = None
TargetPoseA = None
Program = ""
TCPOrientations = []
TargetPointCoordinates = []  # List to store target point coordinates

# Function to apply a Z-axis rotation to a Point3d
def rotate_point_around_z(point, angle_degrees):
    """Rotates a Rhino Point3d around the Z-axis by the given angle in degrees."""
    angle_radians = math.radians(angle_degrees)
    rotation_matrix = rg.Transform.Rotation(angle_radians, rg.Vector3d(0, 0, 1), rg.Point3d(0, 0, 0))
    rotated_point = rg.Point3d(point)
    rotated_point.Transform(rotation_matrix)
    return rotated_point

# Function to convert Rhino Plane to RoboDK Pose (4x4 matrix)
def plane_to_pose(plane):
    """Converts a Rhino plane to a RoboDK pose (4x4 matrix)."""
    pose = rdk.Mat([
        [plane.XAxis.X, plane.YAxis.X, plane.ZAxis.X, plane.OriginX],  
        [plane.XAxis.Y, plane.YAxis.Y, plane.ZAxis.Y, plane.OriginY],
        [plane.XAxis.Z, plane.YAxis.Z, plane.ZAxis.Z, plane.OriginZ],
        [0, 0, 0, 1]
    ])
    return pose

# Function to format the orientation of the TCP as strings for easy reporting
def format_tcp_orientation(plane, milestone):
    """Formats the TCP orientation (X, Y, Z axes) for a given milestone."""
    x_axis = plane.XAxis
    y_axis = plane.YAxis
    z_axis = plane.ZAxis
    return f"TCP orientation at {milestone}:\n  X-axis: {x_axis}\n  Y-axis: {y_axis}\n  Z-axis: {z_axis}"

# Function to format the target point coordinates {x, y, z} for reporting
def format_target_coordinates(plane, milestone):
    """Formats the target point coordinates as a string for a given milestone."""
    return f"{plane.Origin.X}, {plane.Origin.Y}, {plane.Origin.Z}"

# Check required inputs before proceeding
if not RobotName:
    SuccessMessage = "Error: RobotName is required."
elif not isinstance(TargetPoint0, rg.Point3d):
    SuccessMessage = "Error: TargetPoint0 must be a Rhino Point3d."
elif not isinstance(TargetPointA, rg.Point3d):
    SuccessMessage = "Error: TargetPointA must be a Rhino Point3d."
elif UpdateRoboDK is None:
    SuccessMessage = "Error: UpdateRoboDK toggle is required."
elif not UpdateRoboDK:
    SuccessMessage = "UpdateRoboDK is set to False. No action taken."
else:
    # Connect to RoboDK only if UpdateRoboDK is True
    RDK = rl.Robolink()  # Initialize RoboDK connection
    SuccessMessage = "Connected to RoboDK."
    
    # Retrieve the robot by name
    robot = RDK.Item(RobotName, rl.ITEM_TYPE_ROBOT)
    
    if not robot.Valid():
        SuccessMessage += f"\nError: Could not find {RobotName} in RoboDK."
    else:
        SuccessMessage += f"\nFound robot '{robot.Name()}' in RoboDK."
        
        # Get the robot's base and tool
        robot_base = robot.Parent()
        tool = robot.getLink(rl.ITEM_TYPE_TOOL)
        
        # Check if the robot base and tool are valid
        if not robot_base.Valid():
            SuccessMessage += "\nError: Robot's base not found."
        else:
            SuccessMessage += f"\nRobot base: {robot_base.Name()}"

        if not tool.Valid():
            SuccessMessage += "\nError: Robot's tool not found."
        else:
            SuccessMessage += f"\nRobot tool: {tool.Name()}"

        # Enable collision detection in RoboDK
        RDK.setCollisionActive(1)
        
        if not robot_base.Valid() or not tool.Valid():
            SuccessMessage += "\nCannot proceed without valid base and tool."
        else:
            # Apply the user-defined Z-axis rotation to the TargetPoint0 and TargetPointA
            # If BaseRotationZ is 0, no rotation will be applied
            if 'BaseRotationZ' in globals() and isinstance(BaseRotationZ, (int, float)):
                rotated_target_point_0 = rotate_point_around_z(TargetPoint0, BaseRotationZ)
                rotated_target_point_A = rotate_point_around_z(TargetPointA, BaseRotationZ)
            else:
                # No rotation needed, use the original points
                rotated_target_point_0 = TargetPoint0
                rotated_target_point_A = TargetPointA

            # Define the target points (TargetPoint0 and TargetPointA)
            # For TargetPoint0, the Z-axis should point downwards (towards [0, 0, -1])
            z_axis_0 = rg.Vector3d(0, 0, -1)  # TCP faces downwards at TargetPoint0
            x_axis_0 = rg.Vector3d(1, 0, 0)   # X-axis remains unchanged
            y_axis_0 = rg.Vector3d.CrossProduct(z_axis_0, x_axis_0)  # Recalculate Y-axis
            
            # For TargetPointA, the Z-axis should point forward (towards [1, 0, 0]) and Y-axis should point downwards
            z_axis_A = rg.Vector3d(1, 0, 0)   # TCP faces forward at TargetPointA
            y_axis_A = rg.Vector3d(0, 0, -1)  # Y-axis faces downwards at TargetPointA
            x_axis_A = rg.Vector3d.CrossProduct(y_axis_A, z_axis_A)  # Recalculate X-axis to ensure orthogonality

            # Create a plane for the rotated TargetPoint0 (with the TCP facing down)
            TargetPose0 = rg.Plane(rotated_target_point_0, x_axis_0, y_axis_0)
            # Convert TargetPose0 to RoboDK pose
            target_pose_robot_0 = plane_to_pose(TargetPose0)
            
            # Create a plane for the rotated TargetPointA (with the TCP facing forward and Y-axis down)
            TargetPoseA = rg.Plane(rotated_target_point_A, x_axis_A, y_axis_A)
            # Convert TargetPoseA to RoboDK pose
            target_pose_robot_A = plane_to_pose(TargetPoseA)

            # Parse target points and orientations for TargetPoint0 and TargetPointA
            TCPOrientations.append(format_tcp_orientation(TargetPose0, "TargetPoint0"))
            TCPOrientations.append(format_tcp_orientation(TargetPoseA, "TargetPointA"))
            TargetPointCoordinates.append(format_target_coordinates(TargetPose0, "TargetPoint0"))
            TargetPointCoordinates.append(format_target_coordinates(TargetPoseA, "TargetPointA"))

            # Add the movement targets in RoboDK
            target_0 = RDK.AddTarget("TargetPoint0", robot_base, robot)
            target_0.setAsCartesianTarget()
            target_0.setPose(target_pose_robot_0)
            
            target_A = RDK.AddTarget("TargetPointA", robot_base, robot)
            target_A.setAsCartesianTarget()
            target_A.setPose(target_pose_robot_A)

            SuccessMessage += "\nCreating program in RoboDK..."
            program_name = "MoveToTargetProgram"
            program = RDK.AddProgram(program_name, robot)
            
            program.setFrame(robot_base)  # Set the base frame of the robot
            program.setTool(tool)  # Set the tool of the robot

            # Add movements to the program: TargetPoint0 -> TargetPointA
            program.MoveJ(target_0)  # Move to TargetPoint0 (TCP facing downwards)
            program.MoveJ(target_A)  # Move to TargetPointA (TCP facing forward, Y-axis downwards)

            Program = program_name  # Assign the created program's name to the output
            SuccessMessage += f"\nProgram '{program_name}' created successfully."