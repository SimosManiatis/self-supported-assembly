import robolink as rl       
import robodk as rdk        
import Rhino.Geometry as rg 
import math                 
SuccessMessage = ""   
BasePosition = ""     
JointPoints = []      
JointLines = []       


RDK = rl.Robolink()
robot = RDK.Item(RobotName, rl.ITEM_TYPE_ROBOT)
if not robot.Valid():
    
    SuccessMessage = f"Error: Could not find robot '{RobotName}' in RoboDK."
else:
    
    SuccessMessage = f"Connected to robot '{RobotName}' in RoboDK."

    
    if PointIndex >= len(TablePoints) or PointIndex < 0:
        SuccessMessage = f"Error: Point index {PointIndex} is out of bounds."
    else:
        
        point = TablePoints[PointIndex]
        
        
        x = float(point.X)
        y = float(point.Y)
        z = float(point.Z)
        
        
        if SetBase:
           

            
            rz_deg = RotationZ  

            
            rz_rad = math.radians(rz_deg)

           
            rotation_matrix = rdk.rotz(rz_rad)

           
            translation_matrix = rdk.transl(x, y, z)

            
            base_pose = translation_matrix * rotation_matrix

            # === End of Code for RotationZ ===

            # Get the robot's base (parent item in RoboDK)
            robot_base = robot.Parent()

            # Check if robot base is valid before setting pose
            if robot_base.Valid():
                # Set the robot base pose in RoboDK
                robot_base.setPose(base_pose)

                
                BasePosition = f"Base set at: X={x}, Y={y}, Z={z}, RotationZ={rz_deg} degrees"
                SuccessMessage = f"Robot '{RobotName}' base set at Point {PointIndex} with RotationZ={rz_deg} degrees successfully."
            else:
                
                SuccessMessage = "Error: Could not find or access the robot base."
                BasePosition = ""
        else:
            
            robot_base = robot.Parent()
            if robot_base.Valid():
                
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
