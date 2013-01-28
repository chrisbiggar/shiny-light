#
# starter script for roboz

from optparse import OptionParser
import sys

if sys.version_info[0] == 3:
    print "Python 3 is not supported"            
    sys.exit(1)
elif sys.version_info[1] <=5:
	print "Python 2.6+ is required"
	sys.exit(1)

parser = OptionParser()
parser.add_option("-e", "--editor", dest="editor", default=False, action="store_true",
					help="start the level editor")
parser.add_option("-d", "--debug", dest="debug", default=False, action="store_true", 
					help="run in debug mode")
parser.add_option("-r", "--showfps", dest="showfps", default=False, action="store_true",
					help="show frame rate per second")

(options, args) = parser.parse_args()

if __name__ == '__main__':
	if options.debug == False:
		import pyglet
		pyglet.options['debug_gl'] = False
		
	if options.editor == True:
		from editor import leveleditor
		leveleditor.LevelEditor(options).run()
	else:
		from game import main
		main.Game(options).run()
