# SolarGen-Blender
Procedural solar array generator for Blender 5, built with Geometry Nodes and Python.

# SolarGen — Procedural Solar Array Generator for Blender

**SolarGen V1.0.0** is a Blender add-on built using Python and Geometry Nodes that generates customizable solar panel arrays with procedural layouts, adjustable panel configurations, and supporting geometry.

Designed to streamline environment creation and demonstrate procedural asset generation workflows for technical art and game development.

![SolarGen Hero Render](media/hero.jpg)

## Features

- **Procedural Scaling:** Resize the controller in Object Mode to automatically adjust panel counts while maintaining individual panel dimensions.
- **Multiple Layouts:** Generate rectangular, circular, and hexagonal solar arrays.
- **Adjustable Panel Tilt:** Rotate panels around their lower edge with accompanying support structures.
- **Customizable Spacing:** Control the gaps between panels.
- **Panel Density:** Randomly remove panels to create different distributions.
- **Random Seed:** Generate reproducible variations in panel placement.
- **Procedural Backing and Frames:** Automatically adapt the backing geometry and border to the array layout.
- **Multiple Independent Generators:** Create and customize multiple solar arrays in the same Blender scene.
- **Editable Source Assets:** Advanced users can access the underlying panel and support meshes.

## Gallery

### Layout Variations

![SolarGen Layout Variations](media/shapes.jpg)

Rectangular, circular, and hexagonal configurations generated using the same procedural system.

### Density and Supporting Geometry

![SolarGen Density Example](media/density.jpg)

Reduced panel density reveals the backing structure, frames, and mechanical supports.

## Installation

**Requirements:** Blender 5.0 or later (developed and tested with Blender 5.0).

1. Download the SolarGen add-on ZIP from the GitHub Releases section.
2. Open Blender.
3. Navigate to **Edit → Preferences → Add-ons**.
4. Select **Install from Disk** from the add-ons menu.
5. Choose the downloaded ZIP file.
6. Enable SolarGen if necessary.

*Note: Do not extract the add-on ZIP before installing it.*

## How to Use

1. Open Blender's 3D Viewport.
2. Press **N** to open the sidebar.
3. Select the **SolarGen** tab.
4. Click **Add Generator**.
5. Select the generated controller object.
6. Scale the controller in **Object Mode** to change the array dimensions and panel count.
7. Open the **Modifiers** tab to adjust the procedural settings.

You can add multiple generators and customize each independently.

### Advanced Customization

The add-on includes a hidden `SolarGen_Internal` collection containing the source meshes used by the generator.

Use **Show Source Assets** in the SolarGen sidebar to access these meshes for customization.

Changes to shared source assets can affect all generators that reference them.

## Technical Implementation

SolarGen combines Blender's Geometry Nodes with Python scripting.

- **Geometry Nodes:** Procedural layouts, point distribution, instancing, panel rotation, backing geometry, and frame generation.
- **Python:** Add-on registration, asset loading, controller creation, sidebar interface, and asset management.
- **Asset Reuse:** Shared source meshes and node groups reduce unnecessary duplication.
- **Procedural Geometry:** Convex Hull operations generate backing geometry that adapts to different array shapes.

## Demo

A demonstration video showing the generator's interactive workflow will be added soon.

## Version

**V1.0.0 — Initial Release**

Includes rectangular, circular, and hexagonal layouts, adjustable tilt and spacing, density controls, procedural supporting geometry, and Blender sidebar integration.

## Author

**Jaswinder Singh**

Applied Computer Science | Technical Art & Game Development

Built as a technical-art portfolio project using Blender, Geometry Nodes, and Python.
