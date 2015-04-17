# Helper function to determine if a point is cointained within a box of the mesh
def point_in_box(point, box):
	x1, x2, y1, y2 = box
	px, py = point
	dx1 = x1 - px
	dx2 = x2 - px
	dy1 = y1 - py
	dy2 = y2 - py
	# Deltas being opposite indicates that the point is within the given bounds
	# (x1<=px<=x2 or x2<=px<=x1) and (y1<=py<=y2 or y2<=py<=y1)
	return (dx1*dx2 <= 0 and dy1*dy2 <= 0)

# Helper function to return the box for a given point
def box_from_point(point, mesh):
	for box in mesh['boxes']:
		if point_in_box(point, box):
			return box

# Constrain a point to a box
def nearest_point_in_box(point, box):
	px, py = point
	x1, x2, y1, y2 = box
	# Constrain to top right
	px = min(px, x2)
	py = min(py, y2)
	# Constrain to bottom left
	px = max(px, x1)
	py = max(py, y2)
	return (px, py)

def find_path(source_point, dest_point, mesh):
	# A list of points used to draw the path found
	path = []
	# Just draw the straight line path for testing
	path.append((source_point, dest_point))
	# A list of boxes visited in the nav mesh
	visited_nodes = []
	# Show the source and destination box
	visited_nodes.append(box_from_point(source_point, mesh))
	visited_nodes.append(box_from_point(dest_point, mesh))

	visited_nodes = bfs(source_box, dest_box, mesh)
	return (path, visited_nodes)

def bfs(source_point, dest_point, mesh):
	source = box_from_point(source_point, mesh)
	dest = box_from_point(dest_point, mesh)
	queue = [source]
	visited = []
	paths = 
	goal_found = False
	while queue:
		node = queue.pop(0)
		visited.append(node)

		if node == dest:
			print "Goal found"
			goal_found = True
			break

		for adjacent_box in mesh["adj"][node]:
			if adjacent_box not in visited and adjacent_box not in queue:
				queue.append(adjacent_box)

	if goal_found is False:
		print "No path!"
		return []
	else:
		return visited
