"""
Stable Collector by Artemonim, 2023
Designed to navigate through a collection of images rendered in Stable Diffusion.

Changelog:
    v0.0.02-alpha:
        TODO: Add normal album viewer
        TODO: Add image viewer
        TODO: Add image metadata viewer
        TODO: Make it executable
        TODO: Change path to the output folder trough the UI
        TODO: Enter a query trough the UI

Known issues:
    - Non-adaptive aspect ratio
    - Grid images oversize error

Future plans:
    - Set type of images to search for (grid, image)
    - Copy found images to a new folder
    - Export images with watermark
    - Export images in optimized

Dependencies:
    - PIL (Pillow)
    - tkinter
    - simplejson (optional)
"""

import os
import PIL.Image as Image
import PIL.ImageTk as ImageTk
import tkinter as tk
try:
    import simplejson as json
except ImportError:
    import json

# Constants
SD_METADATA = ("extras", "parameters", "postprocessing")    # Metadata keys that are used in Stable Diffusion (full?)
LIMITER = 100   # TEST: For testing purposes

# Path to the output folder with images
path = "D:/Stable UI/stable-diffusion-webui/outputs/"   # TODO: Change this trough the UI

# all files that were found
pngs = []

def getPNGs(path):
    files = os.listdir(path)
    for file in files:
        # Check if file is a folder
        if len(pngs) > LIMITER:
            return
        if os.path.isdir(os.path.join(path, file)):
            # If it is a folder, then call the getPNGs function again
            print("Folder found: " + os.path.join(path, file))
            pngs.append(getPNGs(os.path.join(path, file)))
        elif file.endswith(".png"):
            pngs.append(os.path.join(path, file))

        # Check is last value is None and remove it
        if pngs[-1] is None:
            pngs.pop()
        # Check for all backslashes in last value and replace them with forward slashes
        if "\\" in pngs[-1]:
            pngs[-1] = pngs[-1].replace("\\", "/")


# Import png files through PIL
if __name__ == '__main__':
    files = os.listdir(path)
    i = 0
    print("Start working!")
    getPNGs(path)
    # Save pngs to json file
    with open('Index/index.json', 'w') as f:
        json.dump(pngs, f)
    print("\nDone!")
    print(len(pngs), "files found!")

    # Read json file with pngs
    # Look SD_METADATA for metadata keys
    with open('Index/index.json', 'r') as f:
        data = json.load(f)
        # read first file in the json file and print its metadata in pretty format
        # print(json.dumps(Image.open(data[0]).info, indent=4, sort_keys=True))

        query = "jacket"    # TODO: Change this trough the UI
        results = []
        for file in data:
            try:
                if query in Image.open(file).info["parameters"]:
                    print(file)
                    results.append(file)
            except: 
                pass

        # Show results images in tkinter window as a grid
        root = tk.Tk()
        root.title("Stable Collector: " + query + " results")
        windowWidth = 1200
        windowHeight = 800
        targetImageWidth = 200
        targetImageHeight = 200
        root.geometry(f"{windowWidth}x{windowHeight}+0+0")
        root.resizable(True, True)

        for i in range(len(results)):
            img = ImageTk.PhotoImage(Image.open(results[i]).resize((targetImageWidth, targetImageHeight)))
            panel = tk.Label(root, image=img)
            panel.image = img
            panel.grid(row=i//(windowWidth//targetImageWidth), column=i%(windowWidth//targetImageWidth))

        root.mainloop()
