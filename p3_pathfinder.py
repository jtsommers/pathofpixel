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


def find_path(source_point, dest_point, mesh):
	# A list of points used to draw the path found
	path = []
	# Just draw the straight line path for testing
	path.append((source_point, dest_point))
	# A list of boxes visited in the nav mesh
	visited_nodes = []
	# Show the source and destination box
	for box in mesh['boxes']:
		if point_in_box(source_point, box):
			visited_nodes.append(box)
		elif point_in_box(dest_point, box):
			visited_nodes.append(box)
	return (path, visited_nodes)

