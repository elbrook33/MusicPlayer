# Python3 MPD client, using python-mpd2 and PySide (Qt4)

"""
To do:
	- Set font and size (or set line height based on system font size).
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
	return [ extract_name(track) for track in list if extract_name(track) ]

def extract_name( track ):
	if 'name' in track:
		return track['name']
	elif 'title' in track:
		return track['title']
	else:
		return ''

def format_track( track ):
	if 'album' in track and 'artist' in track:
		return track['artist'] + " - " + track['album'] + " - " + extract_name(track)
	elif 'artist' in track:
		return track['artist'] + " - " + extract_name(track)
	else:
		return extract_name(track) if extract_name(track) else '- -'

# Set up event responder
import threading, time

class MyController( QtCore.QObject ):
	# Keep track of currently playing song. A thread polls MPD every second
	_currentSong = {}
	appIsDone = False
	onStateChanged = QtCore.Signal()
	playProgress = QtCore.Signal()
	
	def doPolling( self ):
		while not self.appIsDone:
			song = mpd.currentsong()
			if song != self._currentSong:
				self._currentSong = song
				self.onStateChanged.emit()	# Triggers QML updates (by QtCore)
			self.status = mpd.status()
			if( self.status['state'] == 'play' or self.status['state'] == 'pause' ):
				self.playProgress.emit()
			time.sleep( 1 )	# Wait one second
	
	def startPolling( self ):
		thread = threading.Thread( target=self.doPolling )
		thread.start()
	
	def finishUp( self ):	# Thread needs to stop when app closes. Triggered by aboutToQuit
		self.appIsDone = True	
	
	# Hooks to let QML access current song info
	def private_currentSong( self ):
		song = mpd.currentsong()
		return format_track(song)
	
	def private_songIndex( self ):
		try:
			return [format_track(i) for i in tracks].index( self.private_currentSong() )
			# Need to compare strings because original objects are references, I guess
		except ValueError:
			return -1
	
	currentSong = QtCore.Property( str, private_currentSong, notify=onStateChanged )
	currentSongIndex = QtCore.Property( int, private_songIndex, notify=onStateChanged )
	
	# Handle clicks on artist, album and track list items. (These are all triggered in QML.)
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
		self.onStateChanged.emit()	# Updates 'state', so play button becomes pause
	@QtCore.Slot()
	def previous( self ):
		mpd.previous()
		self.onStateChanged.emit()	# Quicker UI refresh (though still waits for MPD)
	@QtCore.Slot()
	def next( self ):
		mpd.next()
		self.onStateChanged.emit()
	def getState( self ):
		return self.status['state']
	state = QtCore.Property( str, getState, notify=onStateChanged )
	
	# Search (filter)
	@QtCore.Slot( str )
	def filterLists( self, query ):
		global tracks
		# Reset first with original copies. (This should be in MyListModel.)
		artistsList.replaceData( self.artistsCopy.list() )
		albumsList.replaceData( self.albumsCopy.list() )
		tracks = self.tracksCopy
		tracksList.replaceData( extract_names( tracks ) )
		# Do filter
		artistsList.filter( query )
		albumsList.filter( query )
		tracksList.filter( query )
		tracks = [ i for i in tracks if query.upper() in extract_name(i).upper() ]
		self.onStateChanged.emit()	# Updates track list highlighting
	
	def resetLists( self ):
		global tracks
		artistsList.replaceData( mpd.list( 'AlbumArtist' ) )
		albumsList.replaceData( mpd.list( 'Album' ) )
		tracks = [ i for i in mpd.search( 'Artist', '' ) if extract_name(i) ]
		tracksList.replaceData( extract_names( tracks ) )
		# Save copies for filter searches
		self.artistsCopy = MyListModel( artistsList.list() )
		self.albumsCopy = MyListModel( albumsList.list() )
		self.tracksCopy = tracks

	
	#Progress bar
	def private_getProgress( self ):
		times = self.status['time'].split( ':' )
		return str( float( times[0] ) / float( times[1] ) )
	songProgress = QtCore.Property( str, private_getProgress, notify=playProgress )

# Set up app (make accessible from QML)
artistsList = MyListModel()	# Qt-compatible object
albumsList = MyListModel()
tracksList = MyListModel()
tracks = []

root.setContextProperty('artistsListModel', artistsList)
root.setContextProperty('albumsListModel', albumsList)
root.setContextProperty('tracksListModel', tracksList)

# Connect and start event responder
controller = MyController()
controller.resetLists()
controller.startPolling()
root.setContextProperty('controller', controller)

# Start app
qmlView.setSource( 'MusicPlayer.qml' )
qmlView.show()
app.aboutToQuit.connect( controller.finishUp )
app.exec_()