import subprocess

def execute_exe(file_path):
    try:
        result = subprocess.run([file_path], check=True, capture_output=True, text=True)
        print("Output:", result.stdout)
        print("Error:", result.stderr)
        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        print("An error occurred:", e)
        return None, str(e)


