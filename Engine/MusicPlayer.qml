import QtQuick 1.0

Column {
	/* Header for controls (eventually) */
	Rectangle {
		id: topHeader
		width: tracksView.width
		height: 32
		color: '#808080'
		
		Text {
			id: currentTrack
			text: controller.currentSong
			font.bold: true
			color: 'white'
			anchors.left: parent.left
			anchors.leftMargin: 10
			anchors.right: controls.left
			anchors.rightMargin: 10
			anchors.bottom: parent.bottom
			height: 20
			verticalAlignment: Text.AlignVCenter
			clip: true
		}
		Row {
			id: controls
			anchors.right: parent.right
			anchors.rightMargin: 10
			spacing: 10
			Rectangle {
				id: previous
				width: 32
				height: 32
				Image {
					source: '../Icons/previous.png'
					anchors.fill: parent
				}
				MouseArea {
					anchors.fill: parent
					onClicked: {
						controller.previous()
			}	}	}
			Rectangle {
				id: playPause
				width: 32
				height: 32
				Image {
					source: controller.state == 'play'? '../Icons/pause.png' : '../Icons/play.png'
					anchors.fill: parent
				}
				MouseArea {
					anchors.fill: parent
					onClicked: {
						controller.togglePlay()
			}	}	}
			Rectangle {
				id: next
				width: 32
				height: 32
				Image {
					source: '../Icons/next.png'
					anchors.fill: parent
				}
				MouseArea {
					anchors.fill: parent
					onClicked: {
						controller.next()
	}	}	}	}	}
	
	/* Divider line */
	Rectangle {
		width: tracksView.width
		height: 1
		color: '#ddd'
	}
	
	/* Top panels: artists and albums browser */
	Row {
		/* Artists */
		Column {
			/* Header */
			Rectangle {
				id: artistsHeader
				width: artistsView.width
				height: 20
				color: '#eee'
				Text {
					text: 'Artists'
					font.bold: true
					anchors.leftMargin: 10
					anchors.topMargin: artistsHeader.height - 20
					anchors.fill: parent
					verticalAlignment: Text.AlignVCenter
				}
				MouseArea {
					anchors.fill: parent
					onClicked: {
						// Clear artist filter
			}	}	}
			/* Divider line */
			Rectangle {
				width: artistsView.width
				height: 1
				color: '#ddd'
			}
			/* List */
			ListView {
				id: artistsView
				width: 400
				height: 300
				clip: true
				
				model: artistsListModel
				highlight: Rectangle { color: 'lightsteelblue' }
				highlightMoveDuration: 1
				currentIndex: -1
				focus: true
				
				onCurrentItemChanged: {
					controller.itemClicked( 'Artist', currentItem.children[0].text, currentIndex )
					albumsView.currentIndex = -1
				}
				
				/* Artist list items */
				delegate: Component {
					Item {
						width: artistsView.width
						height: 20
						Text {
							text: model.item
							anchors.leftMargin: 10
							anchors.rightMargin: 10
							anchors.fill: parent
							verticalAlignment: Text.AlignVCenter
						}
						MouseArea {
							anchors.fill: parent
						MouseArea {
							anchors.fill: parent
							onClicked: {
								artistsView.currentIndex = index
	}	}	}	}	}	}	}
		
		/* Vertical divider line */
		Rectangle {
			width: 1
			height: 1 + artistsHeader.height + 1 + artistsView.height
			color: '#ddd'
		}
		
		/* Albums */
		Column {
			/* Header */
			Rectangle {
				width: albumsView.width
				height: artistsHeader.height
				color: artistsHeader.color
				Text {
					text: 'Albums'
					font.bold: true
					anchors.leftMargin: 10
					anchors.topMargin: artistsHeader.height - 20
					anchors.fill: parent
					verticalAlignment: Text.AlignVCenter
				}
				MouseArea {
					anchors.fill: parent
					onClicked: {
						// Clear album filter
			}	}	}
			/* Divider line */
			Rectangle {
				width: artistsView.width
				height: 1
				color: '#ddd'
			}
			/* Line */
			ListView {
				id: albumsView
				width: artistsView.width
				height: artistsView.height
				clip: true
				
				model: albumsListModel
				highlight: artistsView.highlight
				highlightMoveDuration: 1
				currentIndex: -1
				
				/* Album list items */
				delegate: Component {
					Item {
						width: albumsView.width
						height: 20
						Text {
							text: model.item
							anchors.leftMargin: 10
							anchors.rightMargin: 10
							anchors.fill: parent
							verticalAlignment: Text.AlignVCenter
						}
						MouseArea {
							anchors.fill: parent
							onClicked: {
								albumsView.currentIndex = index
								controller.itemClicked( 'Album', model.item, model.row )
	}	}	}	}	}	}	}

	/* Divider line */
	Rectangle {
		width: tracksView.width
		height: 1
		color: '#ddd'
	}
	
	/* Tracks */
	Column {
		/* Header */
		Rectangle {
			width: tracksView.width
			height: artistsHeader.height
			color: artistsHeader.color
			Text {
				text: 'Tracks'
				font.bold: true
				anchors.leftMargin: 10
				anchors.topMargin: artistsHeader.height - 20
				anchors.fill: parent
				verticalAlignment: Text.AlignVCenter
		}	}
		/* Divider line */
		Rectangle {
			width: tracksView.width
			height: 1
			color: '#ddd'
		}
		/* List */
		ListView {
			id: tracksView
			width: artistsView.width*2 + 1
			height: 200
			clip: true
			
			model: tracksListModel
			highlight: Rectangle { color: 'lightsteelblue' }
			highlightMoveDuration: 1
			currentIndex: controller.currentSongIndex // tracks (global) vs currentSong
			
			/* Track list items */
			delegate: Component {
				Item {
					width: tracksView.width
					height: 20
					Text {
						text: model.item
						anchors.leftMargin: 10
						anchors.rightMargin: 10
						anchors.fill: parent
						verticalAlignment: Text.AlignVCenter
					}
					MouseArea {
						anchors.fill: parent
						onClicked: {
							//tracksView.currentIndex = index // only to speed this up
							controller.itemClicked( 'Track', model.item, model.row )
}	}	}	}	}	}	}