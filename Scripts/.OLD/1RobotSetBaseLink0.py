import robolink as rl       # RoboDK API for communication with RoboDK
import robodk as rdk        # RoboDK tools for pose and mathematical operations
import Rhino.Geometry as rg # Rhino/Grasshopper geometry tools
import math                 # For mathematical calculations

# === Inputs ===
# 1. TablePoints: List of points representing the table (Rhino input).
# 2. RobotName: The name of the robot in RoboDK (e.g., "UR5").
# 3. PointIndex: The index of the point on the table to set as the robot base (e.g., 28 for Point 28).
# 4. SetBase: Boolean toggle to decide whether to set the base position in RoboDK.
# 5. RotationZ: Float value representing the rotation around the Z-axis in degrees (controlled by a slider).

# === Outputs ===
# SuccessMessage: String indicating the success or failure of the script.
# BasePosition: String describing the robot base position and orientation.
# JointPoints: List of Rhino.Geometry.Point3d representing the positions of robot joints for visualization.
# JointLines: List of Rhino.Geometry.Line representing the connections between joints for visualization.

# Initialize outputs
SuccessMessage = ""   # Message indicating the success or failure of the script
BasePosition = ""     # String describing the robot base position and orientation
JointPoints = []      # List to store the positions of robot joints for visualization
JointLines = []       # List to store lines between joints for visualization

# Initialize RoboDK connection
RDK = rl.Robolink()

# Get the robot by name from RoboDK
robot = RDK.Item(RobotName, rl.ITEM_TYPE_ROBOT)

# Check if the robot is found and valid
if not robot.Valid():
    # If robot is not found, update the success message
    SuccessMessage = f"Error: Could not find robot '{RobotName}' in RoboDK."
else:
    # If robot is found, confirm connection
    SuccessMessage = f"Connected to robot '{RobotName}' in RoboDK."

    # Check if the provided PointIndex is within the valid range
    if PointIndex >= len(TablePoints) or PointIndex < 0:
        SuccessMessage = f"Error: Point index {PointIndex} is out of bounds."
    else:
        # Get the selected point from TablePoints based on PointIndex
        point = TablePoints[PointIndex]
        
        # Ensure the point is a valid Rhino.Geometry.Point3d and extract coordinates
        x = float(point.X)
        y = float(point.Y)
        z = float(point.Z)
        
        # Check if the SetBase toggle is True to set the robot base
        if SetBase:
            # === Code for setting Rotation around Z-axis ===

            # Get the rotation angle around Z-axis from the input (in degrees)
            rz_deg = RotationZ  # Rotation around Z-axis in degrees

            # Convert rotation angle from degrees to radians
            rz_rad = math.radians(rz_deg)

            # Create the rotation matrix around Z-axis using RoboDK's function
            rotation_matrix = rdk.rotz(rz_rad)

            # Create the translation matrix to move the base to the desired position
            translation_matrix = rdk.transl(x, y, z)

            # Combine translation and rotation to create the base pose
            base_pose = translation_matrix * rotation_matrix

            # === End of Code for RotationZ ===

            # Get the robot's base (parent item in RoboDK)
            robot_base = robot.Parent()

            # Check if robot base is valid before setting pose
            if robot_base.Valid():
                # Set the robot base pose in RoboDK
                robot_base.setPose(base_pose)

                # Update outputs with the new base position and rotation
                BasePosition = f"Base set at: X={x}, Y={y}, Z={z}, RotationZ={rz_deg} degrees"
                SuccessMessage = f"Robot '{RobotName}' base set at Point {PointIndex} with RotationZ={rz_deg} degrees successfully."
            else:
                # If robot base is not valid, update the success message
                SuccessMessage = "Error: Could not find or access the robot base."
                BasePosition = ""
        else:
            # If SetBase is False, output the current base position without setting it
            robot_base = robot.Parent()
            if robot_base.Valid():
                # Get the current base pose from RoboDK
                current_base_pose = robot_base.Pose()
                # Extract the translation components (position)
                current_position = current_base_pose.Pos()
                # Extract rotation angles around X, Y, Z axes (in radians)
                rx_rad, ry_rad, rz_rad = rdk.pose_2_xyzrpy(current_base_pose)[3:]  # Angles in radians
                # Convert rotation around Z-axis from radians to degrees
                rz_deg = math.degrees(rz_rad)
                # Update the BasePosition output with current position and rotation
                BasePosition = f"Current base position: X={current_position[0]}, Y={current_position[1]}, Z={current_position[2]}, RotationZ={rz_deg} degrees"
            else:
                # If robot base is not valid, update the BasePosition output
                BasePosition = "Error: Could not retrieve base position."
