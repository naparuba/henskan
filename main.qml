import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls.Material 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs


ApplicationWindow {
    visible: true
    width: 800
    height: 600
    title: "Mangle"

    Material.theme: Material.Dark
    Material.accent: Material.Purple

    // Render for the path list elements
    Component {
        id: file_path_renderer
        Row {
            spacing: 10
            Text {
                color: "white"
                text: full_path
            }
            Text {
                text: size + 'Mo'
            }
        }
    }

    // PROGRESS BAR
    function updateProgressBar(value) {
        progress_bar.value = value
    }

    Component.onCompleted: {
        backend.worker.updateProgress.connect(updateProgressBar)
    }


    RowLayout {
        anchors.fill: parent
        anchors.margins: 10
        ColumnLayout {
            //anchors.fill: parent
            //anchors.margins: 10

            ListView {
                id: file_list
                objectName: "file_list"
                height: 500
                width: 350

                model: file_path_model

                delegate: file_path_renderer

                ScrollBar.vertical: ScrollBar {
                    policy: ScrollBar.AsNeeded
                }

                Rectangle {
                    anchors.fill: parent
                    color: "transparent"
                    border.color: "black"
                    border.width: 1
                    Text {
                        anchors.centerIn: parent
                        text: "Drop files here"
                        visible: file_list.count === 0
                    }
                    Drag.active: true
                    Drag.hotSpot.x: width / 2
                    Drag.hotSpot.y: height / 2
                    DropArea {
                        anchors.fill: parent
                        onDropped: {
                            backend.onFilesDropped(drop.text)
                        }
                    }
                }

            }

        }


        // Middle columns with parameters
        ColumnLayout {
            spacing: 10

            // Part that select between Manga and Webtoon
            RowLayout {
                Rectangle {  // Is a Manga
                    width: 64
                    height: 64
                    color: "green"
                    Button {
                        anchors.fill: parent
                        Image {
                            anchors.fill: parent
                            source: "manga.png"
                        }
                        onClicked: {
                            backend.onButtonManga()
                        }
                    }
                }
                Rectangle {  // Is a Webtoon
                    width: 64
                    height: 64
                    color: "yellow"
                    Button {
                        anchors.fill: parent
                        Image {
                            anchors.fill: parent
                            source: "webtoon.png"
                        }
                        onClicked: {
                            backend.onButtonWebtoon()
                        }
                    }
                }
            }

            RowLayout {
                Rectangle {  // No split
                    width: 64
                    height: 64
                    color: "blue"
                    Button {
                        anchors.fill: parent
                        Image {
                            anchors.fill: parent
                            source: "manga.png"
                        }
                        onClicked: {
                            backend.onButtonNoSplit()
                        }
                    }
                }
                Rectangle {  // Split left then right
                    width: 64
                    height: 64
                    color: "purple"
                    Button {
                        anchors.fill: parent
                        Image {
                            anchors.fill: parent
                            source: "manga.png"
                        }
                        onClicked: {
                            backend.onButtonSplitRightThenLeft()
                        }
                    }
                }
                Rectangle {// Split right then left
                    width: 64
                    height: 64
                    color: "grey"
                    Button {
                        anchors.fill: parent
                        Image {
                            anchors.fill: parent
                            source: "manga.png"
                        }
                        onClicked: {
                            backend.onButtonSplitLeftThenRight()
                        }
                    }
                }
            }

            // DEVICE
            ComboBox {
                width: 200
                model: ["Kindle 1", "Kindle 2/3/Touch", "Kindle 4 & 5", "Kindle DX/DXG", "Kindle Paperwhite 1 & 2", "Kindle Paperwhite 3/Voyage/Oasis", "Kobo Mini/Touch", "Kobo Glo", "Kobo Glo HD", "Kobo Aura", "Kobo Aura HD", "Kobo Aura H2O", "Kobo Libra H2O", "Kobo Elipsa 2E"]
                currentIndex: 12  // Kobo Libra H2O, because it's mine ^^
                onCurrentIndexChanged: {
                    console.log("Current index changed to", currentIndex, "model[currentIndex] =", model[currentIndex])
                    backend.onDeviceChanged(model[currentIndex])
                }
            }

            // TITLE
            TextField {
                id: titleInput
                width: parent.width
                //focus: true   // focus at start?
                placeholderText: "Enter title..."
                onTextChanged: {
                    backend.onTitleChanged(titleInput.text)
                }
            }


            // Output
            RowLayout {
                Button {
                    text: "Select Directory"
                    onClicked: {
                        backend.selectOutputDirectory()
                    }
                }

                TextField {
                    id: output_directory
                    width: parent.width
                    readOnly: true
                    //text: selectedDirectoryText
                    placeholderText: "Selected Directory"
                }
            }

        }

        // Last column with submit button and progress bar
        ColumnLayout {

            Rectangle { // Convert button
                width: 128
                height: 128
                color: "green"
                Button {
                    anchors.fill: parent
                    Image {
                        anchors.fill: parent
                        source: "manga.png"
                    }
                    onClicked: {
                        backend.onConvertClicked()
                    }
                }
            }


            ProgressBar {
                id: progress_bar
                objectName: "progress_bar"
                width: parent.width
                from: 0
                to: 100
                value: 0  // Set initial value
            }
        }
    }
}
