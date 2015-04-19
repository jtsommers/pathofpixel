try:
    import Queue as Q  # ver. < 3.0
except ImportError:
    import queue as Q

def log(*args):
	print ''.join([str(arg) for arg in args])

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
	py = max(py, y1)
	return (px, py)

def find_path(source_point, dest_point, mesh, algorithm='astar', statusFn=None):
	global status
	# A list of points used to draw the path found
	path = []
	# Just draw the straight line path for testing
	path.append((source_point, dest_point))
	# A list of boxes visited in the nav mesh
	visited_nodes = []
	# Show the source and destination box
	visited_nodes.append(box_from_point(source_point, mesh))
	visited_nodes.append(box_from_point(dest_point, mesh))

	if statusFn: 
		print "Setting status function"
		status = statusFn
	else:
		status = log

	try:
		search = globals()[algorithm]
		print "Searching using " + algorithm
	except:
		print "Search algorithm '", algorithm, "' not found"
		return ([], [])

	return search(source_point, dest_point, mesh)

def dist_to(curr_point, dest_point):
	from math import sqrt

	dx = curr_point[0] - dest_point[0]
	dy = curr_point[1] - dest_point[1]
	return sqrt(dx**2 + dy**2)

def heuristic(curr_point, dest_point):
	return dist_to(curr_point, dest_point)

def astar(source_point, dest_point, mesh):
	frontier = Q.PriorityQueue()
	source = box_from_point(source_point, mesh)
	dest = box_from_point(dest_point, mesh)
	previous = {}
	previous[source] = None
	cost_so_far = {}
	cost_so_far[source] = 0
	detail_points = {}
	detail_points[source] = source_point
	frontier.put((0, source))
	visited = [source]
	goal_found = False

	while not frontier.empty():
		priority, current = frontier.get()
		if current == dest:
			print "Goal found"
			goal_found = True
			break

		for adjacent_box in mesh["adj"].get(current,[]):
			curr_point = detail_points[current]

			next_point = nearest_point_in_box(curr_point, adjacent_box)
			new_cost = cost_so_far[current] + dist_to(curr_point, next_point)		
			if adjacent_box not in cost_so_far or new_cost < cost_so_far[adjacent_box]:
				# Update the path
				#detail_points[adjacent_box] = nearest_point_in_box()
				cost_so_far[adjacent_box] = new_cost
				previous[adjacent_box] = current
				priority = new_cost + heuristic(next_point, dest_point)
				frontier.put((priority, adjacent_box))
				detail_points[adjacent_box] = next_point
				visited.append(adjacent_box)

	if goal_found:
		status("Num visits: ", len(visited))
		# Build the line segments
		path = []
		boxPath = []
		while current:
			boxPath.append(current)
			current = previous[current]
		# Reverse to put the path in order from start to finish
		boxPath.reverse()
		prevBox = None
		p2 = source_point
		for box in boxPath:
			if prevBox:
				p1 = detail_points[prevBox]
				p2 = detail_points[box]
				path.append((p1, p2))
			prevBox = box
		path.append((p2, dest_point))
		return (path, [visited])
	else:
		status("No path!")
		return ([], [[]])

def bistar(source_point, dest_point, mesh):
	frontier = Q.PriorityQueue()
	source = box_from_point(source_point, mesh)
	dest = box_from_point(dest_point, mesh)

	# Initialize previous references to none (break out of path recreation)
	prev = {}
	prev["source"] = {}
	prev["source"][source] = None
	prev["dest"] = {}
	prev["dest"][dest] = None

	# Map the goals to their target points
	target = {}
	target["source"] = dest_point
	target["dest"] = source_point

	# Reverse the goal
	invert = {"source":"dest", "dest":"source"}

	# Initialize the cost so far
	cost_so_far = {}
	cost_so_far[source] = 0
	cost_so_far[dest] = 0

	# Actual points list
	detail_points = {}
	detail_points[source] = source_point
	detail_points[dest] = dest_point

	frontier.put((0, source, "source"))
	frontier.put((0, dest, "dest"))
	visited = [source, dest]
	visited[0] = [source]
	visited[1] = [dest]
	goal_found = False
	middle = None

	while not frontier.empty():
		priority, current, start = frontier.get()
		goal = invert[start]
		if current in prev[goal]:
			print "Goal found in the middle at node: ", current
			goal_found = True
			middle = current
			break

		for adjacent_box in mesh["adj"].get(current,[]):
			curr_point = detail_points[current]

			next_point = nearest_point_in_box(curr_point, adjacent_box)
			new_cost = cost_so_far[current] + dist_to(curr_point, next_point)		
			if adjacent_box not in cost_so_far or new_cost < cost_so_far[adjacent_box]:
				# Update the path
				cost_so_far[adjacent_box] = new_cost
				prev[start][adjacent_box] = current
				priority = new_cost + heuristic(next_point, target[start])
				frontier.put((priority, adjacent_box, start))
				detail_points[adjacent_box] = next_point
				if start == "source":
					visited[0].append(adjacent_box)
				else:
					visited[1].append(adjacent_box)

	if goal_found:
		path_cost = cost_so_far[prev["source"][middle]] + cost_so_far[prev["dest"][middle]] + dist_to(detail_points[prev["source"][middle]], detail_points[prev["dest"][middle]])
		status("Num visits: ", len(visited[0]) + len(visited[1]))
		# Build the line segments
		path = []

		boxPath = []
		current = prev["source"][middle]
		# Build the box path back toward the source
		while current:
			boxPath.append(current)
			current = prev["source"].get(current,[])
		# Reverse the box path to put it in order
		boxPath.reverse()
		# Append the box path from middle to destination
		current = middle
		while current:
			boxPath.append(current)
			current = prev["dest"].get(current,[])

		# Create the path
		prevBox = None
		p2 = source_point
		for box in boxPath:
			if prevBox:
				p1 = detail_points[prevBox]
				p2 = detail_points[box]
				path.append((p1, p2))
			prevBox = box
		path.append((p2, dest_point))

		return (path, visited)
	else:
		status("No path!")
		return ([], [[]])

def bfs(source_point, dest_point, mesh):
	source = box_from_point(source_point, mesh)
	dest = box_from_point(dest_point, mesh)
	queue = [source]
	visited = []
	# Save the path information to each box
	boxPaths = {}
	boxPaths[source] = [source]
	# Save the point at which we enter every box
	detail_points = {}
	detail_points[source] = source_point
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
				# Update the path
				boxPath = list(boxPaths[node])
				boxPath.append(adjacent_box)
				boxPaths[adjacent_box] = boxPath

				# Get the point at which to enter the box
				detail_points[adjacent_box] = nearest_point_in_box(detail_points[node], adjacent_box)

				# Add box to queue
				queue.append(adjacent_box)

	if goal_found:
		# Build the line segments
		path = []
		boxPath = boxPaths[dest]
		prevBox = None
		p2 = source_point
		for box in boxPath:
			if prevBox:
				p1 = detail_points[prevBox]
				p2 = detail_points[box]
				path.append((p1, p2))
			prevBox = box
		path.append((p2, dest_point))
		return (path, [visited])
	else:
		status("No path!")
		return ([], [[]])
