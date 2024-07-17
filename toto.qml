import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    visible: true
    width: 400
    height: 300
    title: "Exemple QStringListModel"

    Component {
        id: file_path_renderer
        Row {
            spacing: 10
            Text { text: full_path }
            Text { text: '$' + size }
        }
    }

    ListView {
        anchors.fill: parent

        model: file_path_model

        delegate: file_path_renderer

        ScrollBar.vertical: ScrollBar {
            policy: ScrollBar.AsNeeded
        }

    }

    Button {
        text: "Add Files"
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        onClicked: backend.add_file_path()
    }
}
