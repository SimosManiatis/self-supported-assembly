import robolink as rl    # RoboDK API for controlling and communicating with RoboDK   
import robodk as rdk     # RoboDK tools, such as matrix operations and other utilities
import Rhino.Geometry as rg  # Import Rhino.Geometry module as rg
import math

# === Inputs ===
# RobotName: Name of the robot in RoboDK (e.g., "UR5")
# UpdateRoboDK: Boolean toggle to execute the script and update RoboDK when True
# PlanesList: List of Rhino Plane objects (each plane contains both target point and orientation)

# Initialize outputs
SuccessMessage = ""
TargetPoses = []  # List of converted poses
Program = ""
TCPOrientations = []
TargetPointCoordinates = []
PlaneExtra = []  # Unreachable planes for other robots to attempt

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
    return f"{plane.OriginX}, {plane.OriginY}, {plane.OriginZ}"

# Check required inputs before proceeding
if not RobotName:
    SuccessMessage = "Error: RobotName is required."
elif not PlanesList or not isinstance(PlanesList, list):
    SuccessMessage = "Error: PlanesList must be a list of Rhino Plane objects."
elif any(not isinstance(plane, rg.Plane) for plane in PlanesList):
    SuccessMessage = "Error: All elements in PlanesList must be Rhino Plane objects."
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
            # Set the robot to its home position before starting
            robot.MoveJ(robot.JointsHome())

            # Get the robot base frame pose
            base_pose = robot_base.Pose()

            # Create a new program
            SuccessMessage += "\nCreating program in RoboDK..."
            program_name = "MoveThroughPlanesProgram"
            program = RDK.AddProgram(program_name, robot)
            program.setFrame(robot_base)  # Set the base frame of the robot
            program.setTool(tool)  # Set the tool of the robot

            # Process each plane in PlanesList independently
            for idx, plane in enumerate(PlanesList):
                # Convert plane to RoboDK pose
                target_pose_robot = plane_to_pose(plane)

                # Adjust the target pose with respect to the robot's base frame
                base_pose_inv = base_pose.inv()
                target_pose_relative = base_pose_inv * target_pose_robot

                # Try a linear movement first
                linear_movement_success = False
                try:
                    robot.MoveL(target_pose_relative, False)  # Simulation mode, does not execute actual motion
                    linear_movement_success = True
                    SuccessMessage += f"\nPlane {idx+1} reachable with linear movement."
                except Exception as e:
                    SuccessMessage += f"\nPlane {idx+1} unreachable with linear movement. Error: {str(e)}"
                    
                    # Attempt a joint movement if linear movement fails
                    try:
                        robot.MoveJ(target_pose_relative, False)  # Simulation mode, does not execute actual motion
                        SuccessMessage += f"\nPlane {idx+1} reachable with joint movement."
                    except Exception as e:
                        SuccessMessage += f"\nPlane {idx+1} unreachable with both linear and joint movements. Error: {str(e)}"
                        PlaneExtra.append(plane)  # Add unreachable plane to PlaneExtra for another robot
                        continue  # Skip this plane and move to the next one

                # Store the pose
                TargetPoses.append(target_pose_relative)

                # Format TCP orientation and coordinates for reporting
                milestone = f"Plane {idx+1}"
                TCPOrientations.append(format_tcp_orientation(plane, milestone))
                TargetPointCoordinates.append(format_target_coordinates(plane, milestone))

                # Add the movement target in RoboDK
                target_name = f"Plane_{idx+1}"
                target = RDK.AddTarget(target_name, robot_base, robot)
                target.setAsCartesianTarget()
                target.setPose(target_pose_relative)

                # Add the correct type of movement to the program
                if linear_movement_success:
                    program.MoveL(target)  # Add the successful linear movement to the program
                else:
                    program.MoveJ(target)  # Add the fallback joint movement to the program

            Program = program_name  # Assign the created program's name to the output
            SuccessMessage += f"\nProgram '{program_name}' created successfully."