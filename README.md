# FlowchartMaker

A simple desktop application for creating and managing flowcharts with common flowchart elements such as processes, decisions, terminators, and input/output symbols. You can connect these elements with arrows and save or load your flowcharts as JSON files. While it lacks some common functionality, this project effectively serves its purpose as a Python demo and showcases the essential concepts.

## Features

- Add various shapes: Process, Decision, Terminator, I/O
- Connect shapes with arrows
- Move shapes around and arrows remain connected
- Remove arrows with a double-click
- Save and load flowcharts in JSON format

## Installation

1. Clone this repository:

   ```
   git clone https://github.com/kikres/FlowchartMaker.git
   cd flowchart-creator
   ```

2. Install dependencies:

   ```
   pip install PySide6
   ```

## Usage

To run the application, use the following command:

```
python app.py
```

## Functionality

- **Add Shapes**: Use the toolbar on the right side of the window to add flowchart shapes such as Process, Decision, Terminator, and I/O to the canvas.
- **Connect Shapes**: Click and drag between the nodes (small circles on the edges of shapes) to create arrows between them.
- **Move Shapes**: Click and drag shapes to move them around. Arrows will remain connected to their respective nodes.
- **Remove Arrows**: Double-click on an arrow to remove it from the flowchart.
- **Save**: Click the "Save" button in the toolbar to save the current flowchart to a JSON file.
- **Load**: Click the "Load" button to load a previously saved flowchart from a JSON file.

## File Formats

Flowcharts are saved as JSON files with the following structure:

```
{
    "shapes": [
        {
            "shape_type": "Process",
            "x": 100,
            "y": 150,
            "width": 130,
            "height": 80,
            "text": "Process Name"
        }
    ],
    "arrows": [
        {
            "start_shape_index": 0,
            "start_node_index": 1,
            "end_shape_index": 1,
            "end_node_index": 0
        }
    ]
}
```
