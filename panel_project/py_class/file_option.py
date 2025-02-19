import os


def edit_file(file_path, new_content=None):
    if new_content is not None:
        with open(file_path, 'w') as file:
            file.write(new_content)
    else:
        with open(file_path, 'r') as file:
            return file.read()

def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)

def download_file(file_path):
    pass

def rename_file(file_path, new_name):
    if os.path.exists(file_path):
        new_path = os.path.join(os.path.dirname(file_path), new_name)
        os.rename(file_path, new_path)


