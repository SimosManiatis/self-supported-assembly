import re

def convert_script_to_urp(script_file_path, urp_save_path):
    """
    Convert a .script file to a .urp XML-based format.
    
    :param script_file_path: Path to the .script file
    :param urp_save_path: Path to save the generated .urp file
    """
    try:
        with open(script_file_path, 'r') as script_file:
            script_content = script_file.read()

        # Start creating the URP program
        urp_program = """<?xml version="1.0" encoding="UTF-8"?>
<program>
    <RobotProgram name="ConvertedProgram" runonload="false">
"""
        
        # Extract the set_tcp command
        tcp_match = re.search(r'set_tcp\(p\[(.*?)\]\)', script_content)
        if tcp_match:
            tcp_values = tcp_match.group(1).split(',')
            urp_program += f"""
        <set_tcp>
            <pose x="{tcp_values[0]}" y="{tcp_values[1]}" z="{tcp_values[2]}" rx="{tcp_values[3]}" ry="{tcp_values[4]}" rz="{tcp_values[5]}"/>
        </set_tcp>
"""
        
        # Extract the set_standard_digital_out commands
        digital_out_commands = re.findall(r'set_standard_digital_out\((\d+),\s*(True|False)\)', script_content)
        for out_id, state in digital_out_commands:
            urp_program += f'        <set_digital_out id="{out_id}" state="{state.lower()}"/>\n'
        
        # Extract move commands (assuming movej is used here as an example)
        move_commands = re.findall(r'movej\(\[(.*?)\],(.*?),(.*?),(.*?),(.*?)\)', script_content)
        for command in move_commands:
            joint_values = command[0].split(',')
            accel_radss = command[1].strip()
            speed_rads = command[2].strip()
            blend_radius_m = command[4].strip()
            urp_program += f"""
        <movej joint_1="{joint_values[0]}" joint_2="{joint_values[1]}" joint_3="{joint_values[2]}"
               joint_4="{joint_values[3]}" joint_5="{joint_values[4]}" joint_6="{joint_values[5]}"
               a="{accel_radss}" v="{speed_rads}" blend_radius="{blend_radius_m}"/>
"""
        
        # End the URP program
        urp_program += """
    </RobotProgram>
</program>
"""
        
        # Write the generated URP to a file
        with open(urp_save_path, 'w') as urp_file:
            urp_file.write(urp_program)
        
        print(f"Successfully converted '{script_file_path}' to '{urp_save_path}'.")
    
    except FileNotFoundError:
        print(f"Error: The file '{script_file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
script_file_path = r"C:\Users\mania\Desktop\MoveThroughPlanesProgram.script"
urp_save_path = r"C:\Users\mania\Desktop\hello.urp"

# Convert the file
convert_script_to_urp(script_file_path, urp_save_path)
