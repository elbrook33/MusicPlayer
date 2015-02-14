# Boilerplate PySide code

import sys
from PySide import QtCore, QtGui, QtDeclarative

# Classes
class MyListModel( QtCore.QAbstractListModel ):
	COLUMNS = ( 'item',  'row' )
	
	def __init__( self, list ):
		QtCore.QAbstractListModel.__init__(self)
		self._things = [ MyListWrapper(i) for i in list ]
		self.setRoleNames( dict( enumerate( MyListModel.COLUMNS ) ) )
	
	def rowCount( self, parent=QtCore.QModelIndex() ):
		return len( self._things )
	
	def data( self, index, role ):
		if index.isValid():
			if role == 0:	# 'item'
				return self._things[ index.row() ].name
			elif role == 1:	# 'row'
				return index.row()
		return None
	
	def replaceData( self, list ):
		self.beginResetModel()
		self._things = [ MyListWrapper(i) for i in list if i ]
		self.endResetModel()

class MyListWrapper( QtCore.QObject ):
	def __init__( self, item ):
		QtCore.QObject.__init__(self)
		self._thing = item
	
	def getName( self ):
		return self._thing
	
	changed = QtCore.Signal()
	name = QtCore.Property( str, getName, notify=changed )