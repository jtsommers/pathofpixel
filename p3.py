import os.path
import sys
import p3_interactive

# Standard format for help option message
def default(str):
	return str + ' [Default: %default]'

DEFAULT_SUBSAMPLES = {
	"dungeon":8,
	"ucsc_banana_slug":1
}

EXTENSIONS = [
	"-orig.gif",
	".png",
	".png.mesh.png"
]

if __name__ == '__main__':
	# Add command line options
	from optparse import OptionParser
	usageStr = """     python %prog <options>
Examples:   (1) python %prog -a bistar -m dungeon -s 8
                - starts a GUI the dungeon example using bi-directional A* search
"""
	parser = OptionParser(usageStr)

	parser.add_option('-a', '--algorithm', help=default('Search algorithm to use'), default='astar')
	parser.add_option('-m', '--map', help='MAP_FILE name without extension (also omit "-orig")', metavar='MAP_FILE', default='dungeon')
	# No default for subsample, allows for using defaults based on an image name
	parser.add_option('-s', '--subsample', help='Scale down a large source image by SCALE_FACTOR', metavar='SCALE_FACTOR', type='int')

	(options, args) = parser.parse_args()

	# Find the actual filename to use
	mapfile = None
	datafile = None
	
	for e in EXTENSIONS:
		filename = options.map + e
		if os.path.isfile(filename):
			mapfile = filename
			break

	if not mapfile:
		print "Error: could not find map image for map named '", options.map, "'"
		sys.exit(-1)

	datafile = options.map + ".png.mesh.pickle"
	if not os.path.isfile(datafile):
		print "Error: map data file not found: ", datafile
		sys.exit(-1)

	subsample = options.subsample
	if not subsample:
		if options.map in DEFAULT_SUBSAMPLES:
			subsample = DEFAULT_SUBSAMPLES[options.map]
		else:
			subsample = 1

	# Start the program
	p3_interactive.initialize(mapfile, datafile, subsample, options.algorithm)
