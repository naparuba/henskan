import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls.Material 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs



ApplicationWindow {
    visible: true
    width: 840
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
        ui_controller.worker.updateProgress.connect(updateProgressBar)
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
                            ui_controller.onFilesDropped(drop.text)
                        }
                    }
                }

            }

        }


        // Middle columns with parameters
        ColumnLayout {
            spacing: 10

            RowLayout {
                Rectangle {  // Is a Manga
                    id: manga_rectangle
                    objectName: "manga_rectangle"
                    width: 64
                    height: 64
                    color: "green"  // enable by default
                    Button {
                        anchors.fill: parent
                        Image {
                            id: manga_button_image
                            anchors.fill: parent
                            source: "mangle/img/manga.png"
                        }
                        onClicked: {
                            ui_controller.onButtonManga()
                        }
                    }
                }
                Rectangle {  // Is a Webtoon
                    id: webtoon_rectangle
                    objectName: "webtoon_rectangle"
                    width: 64
                    height: 64
                    color: "grey"
                    Button {
                        anchors.fill: parent
                        Image {
                            anchors.fill: parent
                            source: "mangle/img/webtoon.png"
                        }
                        onClicked: {
                            ui_controller.onButtonWebtoon()
                        }
                    }
                }
            }

            // separator
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 1
                color: "purple"
            }

            // Split line
            RowLayout {
                Rectangle {  // No split
                    id: no_split_rectangle
                    objectName: "no_split_rectangle"
                    width: 64
                    height: 96
                    color: "green"
                    Button {
                        anchors.fill: parent
                        Image {
                            anchors.fill: parent
                            source: "mangle/img/no-split.png"
                        }
                        onClicked: {
                            ui_controller.onButtonNoSplit()
                        }
                    }
                }
                Rectangle {  // Split left then right
                    id: split_left_right_rectangle
                    objectName: "split_left_right_rectangle"
                    width: 64
                    height: 96
                    color: "grey"
                    Button {
                        anchors.fill: parent
                        Image {
                            anchors.fill: parent
                            source: "mangle/img/split-left-right.png"
                        }
                        onClicked: {
                            ui_controller.onButtonSplitLeftThenRight()
                        }
                    }
                }
                Rectangle {// Split right then left
                    objectName: "split_right_left_rectangle"
                    id: split_right_left_rectangle
                    width: 64
                    height: 96
                    color: "grey"
                    Button {
                        anchors.fill: parent
                        Image {
                            anchors.fill: parent
                            source: "mangle/img/split-right-left.png"
                        }
                        onClicked: {
                            ui_controller.onButtonSplitRightThenLeft()
                        }
                    }
                }
            }

            // separator
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 1
                color: "purple"
            }

            // DEVICE
            RowLayout {
                ComboBox {
                    Layout.fillWidth: true
                    model: ["Kindle 1", "Kindle 2/3/Touch", "Kindle 4 & 5", "Kindle DX/DXG", "Kindle Paperwhite 1 & 2", "Kindle Paperwhite 3/Voyage/Oasis", "Kobo Mini/Touch", "Kobo Glo", "Kobo Glo HD", "Kobo Aura", "Kobo Aura HD", "Kobo Aura H2O", "Kobo Libra H2O", "Kobo Elipsa 2E"]
                    currentIndex: 12  // Kobo Libra H2O, because it's mine ^^
                    onCurrentIndexChanged: {
                        console.log("Current index changed to", currentIndex, "model[currentIndex] =", model[currentIndex])
                        ui_controller.onDeviceChanged(model[currentIndex])
                    }
                }
            }

            // separator
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 1
                color: "purple"
            }

            // TITLE
            RowLayout {
                TextField {
                    id: title_input
                    objectName: "title_input"
                    Layout.fillWidth: true
                    placeholderText: "Enter title..."
                    color: "white"
                    placeholderTextColor : "red"  // by default not set, will be green when set
                    onTextChanged: {
                        ui_controller.onTitleChanged(title_input.text)
                    }
                }
            }

            // separator
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 1
                color: "purple"
            }

            // Output
            RowLayout {
                Button {
                    text: "⇓"
                    onClicked: {
                        ui_controller.selectOutputDirectory()
                    }
                }

                TextField {
                    id: output_directory_input
                    objectName: "output_directory_input"
                    //width: parent.width
                    Layout.fillWidth: true
                    readOnly: true
                    color : "white"
                    placeholderText: "Selected Directory"
                    placeholderTextColor : "red"  // by default not set, will be green when set
                }
            }

        }

        // Last column with submit button and progress bar
        ColumnLayout {

            Rectangle { // Convert button
                width: 128
                height: 128
                //color: "green"
                Button {
                    anchors.fill: parent
                    Image {
                        anchors.fill: parent
                        source: "mangle/img/shock_off.png"
                    }
                    onClicked: {
                        ui_controller.onConvertClicked()
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
