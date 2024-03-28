import os, time

path = r"./uploads"
now = time.time()

for filename in os.listdir(path):
    if os.path.getmtime(os.path.join(path, filename)) < now - 900:
        if os.path.isfile(os.path.join(path, filename)):
            print(filename)
            os.remove(os.path.join(path, filename))