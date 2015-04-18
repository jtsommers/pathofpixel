import sys
import random
import pickle
import traceback
import Tkinter

import p3_pathfinder

source_point = None
destination_point = None
visited_boxes = [[]]
path = []
algorithm = "astar"

def initialize(map_file, mesh_file, sub, alg="astar"):
  # Messy list of globals, quickest and dirtiest refactor for wrapping this thing in a capable CLI
  global MAP_FILENAME, MESH_FILENAME, SUBSAMPLE, master, small_image, canvas, mesh, algorithm
  MAP_FILENAME = map_file
  MESH_FILENAME = mesh_file
  SUBSAMPLE = sub
  SUBSAMPLE = int(SUBSAMPLE)
  algorithm = alg
  with open(MESH_FILENAME, 'rb') as f:

    mesh = pickle.load(f)

  master = Tkinter.Tk()

  big_image = Tkinter.PhotoImage(file=MAP_FILENAME)
  small_image = big_image.subsample(SUBSAMPLE,SUBSAMPLE)
  BIG_WIDTH, BIG_HEIGHT = big_image.width(), big_image.height()
  SMALL_WIDTH, SMALL_HEIGHT = small_image.width(), small_image.height()

  canvas = Tkinter.Canvas(master, width=SMALL_WIDTH, height=SMALL_HEIGHT)
  canvas.pack()

  canvas.bind('<Button-1>', on_click)

  redraw()
  master.mainloop()

def shrink(values):
  return [v/SUBSAMPLE for v in values]

def redraw():

  canvas.delete(Tkinter.ALL)
  canvas.create_image((0,0), anchor=Tkinter.NW, image=small_image)

  for box in visited_boxes[0]:
    x1,x2,y1,y2 = shrink(box)
    canvas.create_rectangle(y1,x1,y2,x2,outline='pink')
  if len(visited_boxes) > 1:
    for box in visited_boxes[1]:
      x1,x2,y1,y2 = shrink(box)
      canvas.create_rectangle(y1,x1,y2,x2,outline='blue')

  for segment in path:
    x1,y1 = shrink(segment[0])
    x2,y2 = shrink(segment[1])
    canvas.create_line(y1,x1,y2,x2,width=2.0,fill='red')

  if source_point:
    x,y = shrink(source_point)
    canvas.create_oval(y-5,x-5,y+5,x+5,width=2,outline='red')

  if destination_point:
    x,y = shrink(destination_point)
    canvas.create_oval(y-5,x-5,y+5,x+5,width=2,outline='red')


def on_click(event):

  global source_point, destination_point, visited_boxes, path

  if source_point and destination_point:

    source_point = None
    destination_point = None
    visited_boxes = []
    path = []

  elif not source_point:

    source_point = event.y*SUBSAMPLE, event.x*SUBSAMPLE

  else:

    destination_point = event.y*SUBSAMPLE, event.x*SUBSAMPLE

    try:
      path, visited_boxes = p3_pathfinder.find_path(source_point, destination_point, mesh, algorithm) 
    except:
      destination_point = None
      traceback.print_exc()


  redraw()

# Initialize the GUI from command line args if this is the main module
if __name__ == '__main__':
  if len(sys.argv) != 4:
    print "usage: %s map.gif map.mesh.pickle subsample_factor" % sys.argv[0]
    sys.exit(-1)

  _, map_file, mesh_file, sub = sys.argv
  initialize(map_file, mesh_file, sub, algorithm)

