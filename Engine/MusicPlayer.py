# Python3 MPD client, using python-mpd2 and PySide (Qt4)

"""
To do:
	- Upload to github?
	- Set font and size (or set line height based on system font size).
	- Search (or at least type first letters).
	- Show time left (align right?) (mpd.status()['time'] returns 'elapsed:duration')
	- Reset filters. (Could be the first item in lists? Seems like the clean way to do it.)
	- Sort better? (Unicode and 'The')
	- Scrolling inertia is awfully heavy...
"""

# Initialize MPD
from mpd import MPDClient

mpd = MPDClient()
mpd.connect( 'localhost', 6600 )	# Need error handling here

# Initialize Qt
import sys
from PySide.QtGui import *
from PySide.QtDeclarative import *

app = QApplication(sys.argv)
qmlView = QDeclarativeView()
root = qmlView.rootContext()

# Initialize my boilerplate classes
from MusicPlayer_classes import *

# Helper functions
def extract_names( list ):
	names = []
	for track in list:
		names.append( extract_name( track ) )
	return names

def extract_name( track ):
	if 'name' in track:
		return track['name']
	elif 'title' in track:
		return track['title']

def format_track( track ):
	if 'album' in track:
		return track['artist'] + " - " + track['album'] + " - " + extract_name(track)
	elif 'artist' in track:
		return track['artist'] + " - " + extract_name(track)
	else:
		return extract_name(track)

# Set up app
artists = filter( None, mpd.list( 'AlbumArtist' ) )
albums = filter( None, mpd.list( 'Album' ) )
tracks = []	# Start empty. Alternatively: tracks = mpd.search( 'Artist', '' )

# Make accessible from QML
artistsList = MyListModel( artists )	# Qt-compatible object
albumsList = MyListModel( albums )
tracksList = MyListModel( extract_names(tracks) )

root.setContextProperty('artistsListModel', artistsList)
root.setContextProperty('albumsListModel', albumsList)
root.setContextProperty('tracksListModel', tracksList)

# Set up event responder
import threading, time

class MyController( QtCore.QObject ):
	# Keep track of currently playing song. A thread polls MPD every second
	_currentSong = {}
	appIsDone = False
	onStateChanged = QtCore.Signal()
	
	def doPolling( self ):
		while not self.appIsDone:
			song = mpd.currentsong()
			if song != self._currentSong:
				self._currentSong = song
				self.onStateChanged.emit()	# Triggers QML updates (by QtCore settings)
			time.sleep( 1 )	# Wait one second
	
	def startPolling( self ):
		thread = threading.Thread( target=self.doPolling )
		thread.start()
	
	def finishUp( self ):	# Thread needs to stop when app closes. Triggered by aboutToQuit
		self.appIsDone = True	
	
	# Hooks to let QML access current song info
	def private_currentSong( self ):
		song = mpd.currentsong()
		if 'artist' in song:
			return format_track(song)
		else:
			return '- -'
	
	def private_songIndex( self ):
		try:
			return [format_track(i) for i in tracks].index( self.private_currentSong() )
			# Need to compare strings because original objects are references, I guess
		except ValueError:
			return -1
	
	currentSong = QtCore.Property( str, private_currentSong, notify=onStateChanged )
	currentSongIndex = QtCore.Property( int, private_songIndex, notify=onStateChanged )
	
	# Handle clicks on artist, album and track list items. (These are all triggered from QML.)
	@QtCore.Slot( str, str, int )
	def itemClicked( self, type, name, index ):
		global tracks	# Need to save tracks globally for later playback
		if type == 'Artist':
			tracks = mpd.find( 'AlbumArtist', name )
			tracksList.replaceData( extract_names(tracks) )
			albumsList.replaceData( mpd.list( 'Album', 'AlbumArtist', name ) )
		elif type == 'Album':
			tracks = mpd.find( 'Album', name )
			tracksList.replaceData( extract_names(tracks) )
		elif type == 'Track':
			mpd.clear()
			[ mpd.add( track['file'] ) for track in tracks ]
			mpd.play( index )
		self.onStateChanged.emit()	# Updates track list highlighting
	
	# Media player controls (play, pause, previous and next)
	@QtCore.Slot()
	def togglePlay( self ):
		mpd.pause() if self.getState() == 'play' else mpd.play()
		self.onStateChanged.emit()	# Updates 'state', so play button becomes pause etc.
	@QtCore.Slot()
	def previous( self ):
		mpd.previous()
		self.onStateChanged.emit()	# Makes UI refresh quicker (though still waits for MPD)
	@QtCore.Slot()
	def next( self ):
		mpd.next()
		self.onStateChanged.emit()
	def getState( self ):
		return mpd.status()['state']
	state = QtCore.Property( str, getState, notify=onStateChanged )

# Connect and start event responder
controller = MyController()
controller.startPolling()
root.setContextProperty('controller', controller)

# Start app
qmlView.setSource( 'MusicPlayer.qml' )
qmlView.show()
app.aboutToQuit.connect( controller.finishUp )
app.exec_()