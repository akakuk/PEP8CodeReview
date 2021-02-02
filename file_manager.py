import os

def get_paths(path):
    
    path_list = []
    if (os.path.isdir(path)):  
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(".py"):
                    path_list.append(os.path.join(root, file))                 
    elif (os.path.isfile(path) and path.endswith(".py")):
        path_list.append(path)
    else:
        path_list = []

    return path_list