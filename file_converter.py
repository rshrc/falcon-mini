import os
import subprocess

input_folder = 'audio_files0'
output_folder = 'audio_files'

def rename_file(old_name):
    # Replace numbers with words
    number_mapping = {'1': 'one', '2': 'two', '3': 'three', '4': 'four', '5': 'five',
                      '6': 'six', '7': 'seven', '8': 'eight', '9': 'nine', '0': 'zero'}
    new_name = ''
    
    for char in old_name:
        if char.isdigit():
            new_name += number_mapping[char]
        elif char.isalpha():
            new_name += char.lower()
        elif char.isspace():
            new_name += ' '
            
    new_name = new_name.replace('mpeg', '').replace('mpg', '')
    return new_name + '.mp3'

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

for filename in os.listdir(input_folder):
    if filename.lower().endswith('.mpeg') or filename.lower().endswith('.mpg'):
        input_path = os.path.join(input_folder, filename)
        output_filename = rename_file(filename)
        output_path = os.path.join(output_folder, output_filename)
        
        # Construct the FFmpeg command
        cmd = ["ffmpeg", "-i", input_path, "-vn", "-acodec", "libmp3lame", output_path]
        
        # Run the FFmpeg command using subprocess
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        print(f"Converted '{filename}' to '{output_filename}'")

print("Conversion and renaming complete!")
