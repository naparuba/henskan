import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls.Material 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs


ApplicationWindow {
    visible: true

    // Fixed size
    maximumHeight: 600
    maximumWidth: 1024

    minimumHeight: 600
    minimumWidth: 1024

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
                text: full_path.length > 80 ? "..." + full_path.slice(-80) : full_path   // Limit size because dialog is not so big
            }
        }
    }

    // PROGRESS BAR
    function update_progress_bar(value) {
        progress_bar.value = value
    }

    Component.onCompleted: {
        ui_controller.worker.updateProgress.connect(update_progress_bar)
    }


    RowLayout {
        anchors.fill: parent
        anchors.margins: 10
        ColumnLayout {
            id: col_file_list
            objectName: "col_file_list"
            Layout.minimumWidth: 300


            ListView {
                id: file_list
                objectName: "file_list"
                Layout.fillWidth: true
                height: 500

                model: file_path_model

                delegate: file_path_renderer

                ScrollBar.vertical: ScrollBar {
                    policy: ScrollBar.AsNeeded
                }

                Rectangle {
                    anchors.fill: parent
                    color: file_list.count === 0 ? "grey" : "transparent"
                    border.color: file_list.count === 0 ? "black" : "green"
                    border.width: 1
                    Text {
                        id: drag_and_drop_text
                        anchors.centerIn: parent
                        text: "Drag & Drop Your Manga or Webtoon images or directories Here!"
                        color: "purple"
                        visible: file_list.count === 0
                        font.pixelSize: 20

                        // Color animation
                        SequentialAnimation on color {
                            id: sequentialAnimation
                            loops: Animation.Infinite
                            ColorAnimation {
                                to: "green"; duration: 1000
                            }
                            ColorAnimation {
                                to: "purple"; duration: 1000
                            }
                        }

                        // Pulse animation
                        ScaleAnimator {
                            id: scaleAnimator
                            target: drag_and_drop_text
                            from: 1.0
                            to: 1.1
                            duration: 500

                            easing.type: Easing.InOutQuad
                            onRunningChanged: {
                                if (!running) {
                                    // Once the scale up animation completes, start the scale down animation
                                    scaleDownAnimator.start();
                                }
                            }
                        }
                        ScaleAnimator {
                            id: scaleDownAnimator
                            target: drag_and_drop_text
                            from: 1.1
                            to: 1.0
                            duration: 500 // Duration for scaling down to match the scale up duration
                            easing.type: Easing.InOutQuad
                            onRunningChanged: {
                                if (!running) {
                                    // Once the scale up animation completes, start the scale down animation
                                    scaleAnimator.start();
                                }
                            }
                        }
                        Component.onCompleted: {
                            scaleAnimator.start();
                            sequentialAnimation.start();
                        }

                    }
                    Drag.active: true
                    Drag.hotSpot.x: width / 2
                    Drag.hotSpot.y: height / 2
                    DropArea {
                        anchors.fill: parent
                        onDropped: {
                            ui_controller.on_files_dropped(drop.text)
                        }
                    }
                }

            }

        }


        // Middle columns with parameters
        ColumnLayout {
            id: col_parameters
            objectName: "col_parameters"
            Layout.minimumWidth: 220

            spacing: 10

            RowLayout {
                ColumnLayout {
                    RowLayout {

                        Rectangle {  // Is a Manga
                            id: manga_rectangle
                            objectName: "manga_rectangle"
                            width: 64
                            height: 64
                            color: "green"  // enable by default

                            RoundButton {
                                radius: 0
                                anchors.fill: parent
                                Image {
                                    id: manga_button_image
                                    anchors.fill: parent
                                    source: "../img/manga.png"
                                }
                                onClicked: {
                                    ui_controller.on_button_manga()
                                }
                            }
                        }
                        Rectangle {  // Is a Webtoon
                            id: webtoon_rectangle
                            objectName: "webtoon_rectangle"
                            width: 64
                            height: 64
                            color: "grey"

                            RoundButton {
                                radius: 0
                                anchors.fill: parent
                                Image {
                                    anchors.fill: parent
                                    source: "../img/webtoon.png"
                                }
                                onClicked: {
                                    ui_controller.on_button_webtoon()
                                }
                            }
                        }
                    }

                    // Fast message display to help the user know why we did choose one or the other
                    Text {
                        id: manga_or_webtoon_text
                        objectName: "manga_or_webtoon_text"
                        text: ""
                        color: "green"
                        font.pixelSize: 10

                        OpacityAnimator {
                            id: manga_or_webtoon_text_opacity_animation
                            target: manga_or_webtoon_text
                            from: 1.0
                            to: 0.0
                            duration: 10000 // 10 seconds
                            easing.type: Easing.InQuart
                            onRunningChanged: {
                                //if (!running) {
                                // Once the scale up animation completes, start the scale down animation
                                //scaleAnimator.start();
                                //}
                            }
                        }

                        // Reset opacity when text changes to make it visible again
                        onTextChanged: {
                            opacity = 1
                            manga_or_webtoon_text_opacity_animation.start()
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

            // MANGA Split line
            RowLayout {
                id: split_manga_row
                objectName: "split_manga_row"

                ColumnLayout {
                    RowLayout {
                        Rectangle {  // No split
                            id: no_split_rectangle
                            objectName: "no_split_rectangle"
                            width: 64
                            height: 96
                            color: "green"
                            RoundButton {
                                radius: 0
                                anchors.fill: parent
                                Image {
                                    anchors.fill: parent
                                    source: "../img/no-split.png"
                                }
                                onClicked: {
                                    ui_controller.on_button_no_split()
                                }
                            }
                        }
                        Rectangle {  // Split left then right
                            id: split_left_right_rectangle
                            objectName: "split_left_right_rectangle"
                            width: 64
                            height: 96
                            color: "grey"
                            RoundButton {
                                radius: 0
                                anchors.fill: parent
                                Image {
                                    anchors.fill: parent
                                    source: "../img/split-left-right.png"
                                }
                                onClicked: {
                                    ui_controller.on_button_split_left_then_right()
                                }
                            }
                        }
                        Rectangle {// Split right then left
                            objectName: "split_right_left_rectangle"
                            id: split_right_left_rectangle
                            width: 64
                            height: 96
                            color: "grey"
                            RoundButton {
                                radius: 0
                                anchors.fill: parent
                                Image {
                                    anchors.fill: parent
                                    source: "../img/split-right-left.png"
                                }
                                onClicked: {
                                    ui_controller.on_button_split_right_then_left()
                                }
                            }
                        }
                    }


                    // Fast message display to help the user know why we did choose one or the other
                    Text {
                        id: split_manga_row_text
                        objectName: "split_manga_row_text"
                        text: ""
                        color: "green"
                        font.pixelSize: 10

                        OpacityAnimator {
                            id: split_manga_row_text_opacity_animation
                            target: split_manga_row_text
                            from: 1.0
                            to: 0.0
                            duration: 10000 // 10 seconds
                            easing.type: Easing.InQuart
                            onRunningChanged: {}
                        }

                        // Reset opacity when text changes to make it visible again
                        onTextChanged: {
                            opacity = 1
                            split_manga_row_text_opacity_animation.start()
                        }

                    }

                }


            }

            // WEBTOON Split line
            RowLayout {
                id: split_webtoon_row
                objectName: "split_webtoon_row"
                visible: false  // hide by default, will be show if webtoon is detected or selected

                ColumnLayout {
                    Rectangle {  // No split
                        width: 64
                        height: 96
                        color: "green"
                        RoundButton {
                            radius: 0
                            anchors.fill: parent
                            Image {
                                anchors.fill: parent
                                source: "../img/split-webtoon.png"
                            }
                        }
                    }

                    // Fast message display to help the user know why we did choose one or the other
                    Text {
                        id: split_webtoon_row_text
                        objectName: "split_webtoon_row_text"
                        text: ""
                        color: "green"
                        font.pixelSize: 10

                        OpacityAnimator {
                            id: split_webtoon_row_text_opacity_animation
                            target: split_webtoon_row_text
                            from: 1.0
                            to: 0.0
                            duration: 10000 // 10 seconds
                            easing.type: Easing.InQuart
                            onRunningChanged: {}
                        }

                        // Reset opacity when text changes to make it visible again
                        onTextChanged: {
                            opacity = 1
                            split_webtoon_row_text_opacity_animation.start()
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
                    id: device_combo_box
                    objectName: "device_combo_box"
                    Layout.fillWidth: true
                    model: ["Kindle 1", "Kindle 2/3/Touch", "Kindle 4 & 5", "Kindle DX/DXG", "Kindle Paperwhite 1 & 2", "Kindle Paperwhite 3/Voyage/Oasis", "Kobo Mini/Touch", "Kobo Glo", "Kobo Glo HD", "Kobo Aura", "Kobo Aura HD", "Kobo Aura H2O", "Kobo Libra H2O", "Kobo Elipsa 2E"]
                    currentIndex: 12  // Kobo Libra H2O, because it's mine ^^
                    onCurrentIndexChanged: {
                        console.log("Current index changed to", currentIndex, "model[currentIndex] =", model[currentIndex])
                        ui_controller.on_device_changed(model[currentIndex], currentIndex)
                    }
                    //popup.Material.foreground: "red"
                    Material.accent: "green"  // border
                    Material.foreground: "green"  // selected text
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
                    placeholderText: text ? "Title" : "Enter title..."
                    color: "white"
                    placeholderTextColor: "red"  // by default not set, will be green when set
                    onTextChanged: {
                        ui_controller.on_title_changed(title_input.text)
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

                TextField {
                    id: output_directory_input
                    objectName: "output_directory_input"
                    //width: parent.width
                    Layout.fillWidth: true
                    readOnly: true
                    color: "white"
                    placeholderText: text ? "Output Directory" : "Select Directory"
                    placeholderTextColor: "red"  // by default not set, will be green when set

                    MouseArea {
                        anchors.fill: parent
                        onClicked: ui_controller.select_output_directory()
                    }
                }

            }


        }

        // Last column with submit button and progress bar

        ColumnLayout {
            id: col_convert
            objectName: "col_convert"


            Rectangle { // Convert button
                id: convert_rect_button
                objectName: "convert_rect_button"
                width: 128
                height: 128

                RoundButton {
                    radius: 0
                    anchors.fill: parent
                    Image {
                        id: col_convert_img
                        objectName: "col_convert_img"
                        anchors.fill: parent
                        source: "../img/shock_off.png"
                    }
                    onClicked: {
                        ui_controller.on_convert_clicked()
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
