import os

#top = "c:\\python37-32"

top = os.path.dirname(os.path.abspath(__file__))

for root, dirs, files in os.walk(top, topdown=False):
    for name in files:
        if name.endswith(".pyc") or name.endswith(".pyo"):
            print("Removing " + name)
            os.remove(os.path.join(root, name))
    #for name in dirs:
    #    os.rmdir(os.path.join(root, name))
    

#r = input("Done!")
