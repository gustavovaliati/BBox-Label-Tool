BBox-Label-Tool
===============

Environment
----------
- python >= 3.5
- Tested on Ubuntu >= 16.04

Required Ubuntu Packages (apt-get install)
- python3-tk
- python3-pil.imagetk

Run
-------
$ python3 main.py

Usage
-----
0. Modify `classes.txt` file in the project's root path with the list of available annotation classes. Each class goes in a new line.
1. The current tool requires that **the images to be labeled reside in /Images/001, /Images/002, etc. You will need to modify the code if you want to label images elsewhere**.
2. Input a folder number (e.g, 1, 2, 5...), and click `Load`. The images in the folder, along with a few example results will be loaded.
3. To create a new bounding box, left-click to select the first vertex. Moving the mouse to draw a rectangle, and left-click again to select the second vertex.
4. Labels are saved when jumping to `Next` image or changing class.
