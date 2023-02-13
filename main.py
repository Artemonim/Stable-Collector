"""
Stable Collector by Artemonim, 2023
Designed to navigate through a collection of images rendered in Stable Diffusion.

Changelog:
    v0.0.02-alpha:
        True indexation
        Code testing improvements

    v0.1.00-beta:
        TODO: GUI
        TODO: Add normal album viewer
        TODO: Add image viewer
        TODO: Add image metadata viewer
        TODO: Make it .executable
        TODO: Change path to the outputs folder trough the UI
        TODO: Enter a query trough the UI
        True indexation
        TODO: "Rebuild index" button
        TODO: Log file

Known issues:
    - Non-adaptive aspect ratio
    - Grid images oversize error

Future plans:
    - Set type of images to search for (grid, image)
    - Negative query (blacklist)
    - Copy found images to a new folder
    - Export images with watermark
    - Export images in optimized format

Dependencies:
    - PIL (Pillow)
    - tkinter
    - simplejson (optional)
"""

import os
import time

import PIL.Image as Image
import PIL.ImageTk as ImageTk
import tkinter as tk
try:
    import simplejson as json
except ImportError:
    import json

# Constants
SD_METADATA = ("extras", "parameters", "postprocessing")    # Metadata keys that are used in Stable Diffusion (full?)

# TEST VARIABLES
LIMITER = 100
DO_NOT_OPEN = False
AUTO_CLOSE = 2
Image.MAX_IMAGE_PIXELS = None   # TODO: Rewrite this so it doesn't disable protection completely
TEST_QUERIES = ("jacket", "shirt", "hair", "face")

# settings variables    # TODO: Change this trough the UI and save it to a file
searchAreaPath = "D:/Stable UI/stable-diffusion-webui/outputs/"
dontSearchForGrids = True
resetIndexOnStart = True

# Global variables
pngs = []   # List of pngs in the search area


def getPNGs(path):
    files = os.listdir(path)
    for file in files:
        # Check if file is a folder
        if LIMITER != 0 and len(pngs) > LIMITER:
            return
        if dontSearchForGrids:
            if "grid" in file:
                continue
        local_path = os.path.join(path, file).replace("\\", "/")
        if os.path.isdir(os.path.join(path, file)):
            # If it is a folder, then call the getPNGs function again
            print("Folder found: " + local_path)
            getPNGs(os.path.join(path, file))
        elif file.endswith(".png"):
            if local_path not in pngs:
                print("PNG found: " + local_path)
                # append local path and image info to pngs list
                pngs.append([local_path, Image.open(local_path).info["parameters"].split(", ")]
                            if "parameters" in Image.open(local_path).info
                            else [local_path, None])

        # Check is last value is None and remove it
        # if pngs[-1] is None:
        #     pngs.pop()


def isItGrid(line):
    # check if line have word "grid" in it
    if "grid" in line:
        return True

    # with open('Index/index.json', 'r+') as f:
    #     # load json file into data variable
    #     data = json.load(f)
    #     # add new line to data
    #     data.append(line)
    #     # write data to json file
    #     json.dump(data, f)


# Import png files through PIL
if __name__ == '__main__':
    searchArea = os.listdir(searchAreaPath)
    i = 0
    print("Start working!")
    start_time = time.time()    # TEST: Start time of execution

    # Save pngs to json file
    with open('Index/index.json', 'w+') as f:
        if resetIndexOnStart:
            print("Resetting index...")
            f.seek(0)
        else:
            # check if json file is empty
            if os.stat('Index/index.json').st_size != 0:
                pngs = json.load(f)
        getPNGs(searchAreaPath)
        json.dump(pngs, f, indent=4)

    print("\nIndexation done!")
    print(len(pngs), "files found!")

    # Read json file with pngs
    with open('Index/index.json', 'r+') as f:
        # check if pngs list is empty
        if len(pngs) == 0:
            data = json.load(f)
        else:
            data = pngs
        # read first file in the json file and print its metadata in pretty format
        # print(json.dumps(Image.open(data[0]).info, indent=4, sort_keys=True))     # TEST: Print metadata

        # pick query from TEST_QUERIES randomly # TODO: Change this trough the UI
        # query = TEST_QUERIES[int(random() * len(TEST_QUERIES))]
        query = "girl"
        print("Query:", query)
        results = []
        for file in data:
            try:
                for line in file[1]:
                    if query in line:    # Look SD_METADATA for metadata keys
                        print(file)
                        results.append(file[0])
                        break
                    if "\nSteps:" in line:
                        break
            except:
                print("Error: " + file[0])
                pass

        # Show results images in tkinter window as a grid
        root = tk.Tk()
        root.title("Stable Collector: " + query + " results")
        windowWidth = 1600
        windowHeight = 800
        targetImageWidth = 200
        targetImageHeight = 200
        root.geometry(f"{windowWidth}x{windowHeight}+0+0")
        root.resizable(True, True)

        print("Building grid...")
        for i in range(len(results)):
            img = ImageTk.PhotoImage(Image.open(results[i]).resize((targetImageWidth, targetImageHeight)))
            panel = tk.Label(root, image=img)
            panel.image = img
            panel.grid(row=i//(windowWidth//targetImageWidth), column=i%(windowWidth//targetImageWidth))

        if not DO_NOT_OPEN:
            print("Opening window...")
            if AUTO_CLOSE != 0:
                print("Closing window in", AUTO_CLOSE, "seconds...")
                root.after(AUTO_CLOSE * 1000, lambda: root.destroy())

            print("--- %s seconds ---" % (time.time() - start_time))  # TEST: Print time of execution
            root.mainloop()



