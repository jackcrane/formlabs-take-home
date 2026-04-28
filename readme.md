# Formlabs technical interview content

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install git+https://github.com/Formlabs/formlabs-api-python.git#subdirectory=local-api/lib
```

```sh
deactivate
```

## Process outline

### 1. Bring in template content from Formlabs' github examples

### 2. Modifications begin: Creating a scene

```python
scene = preform.api.create_scene(SceneTypeModel(Manual(
    machine_type="FORM-4-0",
    material_code="FLRG1011",
    layer_thickness_mm=ManualLayerThicknessMm("0.1"),
    print_setting="DEFAULT",
)))
```

Above is a standard code snippet pulled from example content. We need to change the machine type to support a Form 4BL, and need to update the material code. The enum values of these fields were not easily discoverable, in online documentation, but I found it easy enough from the `/list-materials` endpoint, then searching for "Form 4BL" in the results. That resulted in a machine type of `FRML-4-0` and material code `FLPTB101`. We know the customer wants 50 micron layer thickness.

```python
scene = preform.api.create_scene(SceneTypeModel(Manual(
    machine_type="FRML-4-0",
    material_code="FLPTB101",
    layer_thickness_mm=ManualLayerThicknessMm("0.05"),
    print_setting="DEFAULT",
)))
```

### 3. Import STL files

We should provide the files to the utility in a folder for ease of use, so we pull from the colocated `teeth` directory. As required by the take home spec, we also set the `repair_behavior` to `REPAIR` for each file.

```python
# Import teeth
teeth_dir = pathlib.Path().resolve() / "teeth"

for file in teeth_dir.iterdir():
    if file.suffix.lower() == ".stl":
        preform.api.import_model(
            scene_id=scene.id,
            import_model_request=models.ImportModelRequest(
                file=str(file),
                repair_behavior="REPAIR"
            )
        )
```

### 4. Auto-* the things

Again, following the spec, we need to auto orient, layout, and support the scene. For orient and layout, we use dental mode.

For auto orient, we use the `tilt` parameter to specify a -15 degree tilt. (I assumed a -15 degree tilt since the spec asks for "tip them *back* 15 degrees".)

For auto layout, we set `lock_rotation` to `True` to ensure the tilt from the previous step is preserved.

For auto support, we use the specified parameters from the spec.

```python
# Auto orient
preform.api.auto_orient(
    scene_id=scene.id,
    auto_orient_request=models.AutoOrientRequest(
        models.DentalMode(mode="DENTAL", tilt=-15)
    )
)

# Auto Layout
preform.api.auto_layout(
    scene_id=scene.id,
    auto_layout_request=models.AutoLayoutRequest(
        mode="DENTAL",
        lock_rotation=True
    )
)

# Auto Support
preform.api.auto_support(
    scene_id=scene.id,
    auto_support_request=models.AutoSupportRequest(
        density=0.85,
        touchpoint_size_mm=0.55,
        raft_type="MINI_RAFT"
    )
)
```

Ultimately, I switched the order to generate supports before running auto layouts to prevent raft collisions.

```python
# Auto orient
preform.api.auto_orient(
    scene_id=scene.id,
    auto_orient_request=models.AutoOrientRequest(
        models.DentalMode(mode="DENTAL", tilt=-15)
    )
)

# Auto Support
preform.api.auto_support(
    scene_id=scene.id,
    auto_support_request=models.AutoSupportRequest(
        density=0.85,
        touchpoint_size_mm=0.55,
        raft_type="MINI_RAFT"
    )
)

# Auto Layout
preform.api.auto_layout(
    scene_id=scene.id,
    auto_layout_request=models.AutoLayoutRequest(
        mode="DENTAL",
        lock_rotation=True
    )
)
```

### 5. Ensure occlusal surfaces are facing away from the build surface

The STL files have their occlusal surfaces facing down, but the spec calls for printing with them facing upwards (away from build tray). To fix this we run a rotate transform on each model at import time to rotate 180 degrees around the X axis.

```python
# Import teeth
...
preform.api.import_model(
    scene_id=scene.id,
    import_model_request=models.ImportModelRequest(
        file=str(file),
        repair_behavior="REPAIR",
        orientation=models.OrientationModel(
            models.EulerAnglesModel(x=180, y=0, z=0)
        )
    )
)
```

### 6. Load printers

Early in the file, we are going to add:

```python
preform.api.discover_devices(
    var_async=True,
    discover_devices_request=models.DiscoverDevicesRequest(
        timeout_seconds=60
    )
)
```

This way it can work in the background to discover printers while we are processing the rest of the scene.

After the scene is ready, we will ask the user which printer they want to print on. I have included a fallback to allow the user to mock a printer in case there is not a printer available during testing.

### 7. Print the scene

Finally, we will send the print command to the printer.

```python
preform.api.call_print(
    scene_id=scene.id,
    print_request=models.PrintRequest(
        printer=selected.ip_address,
        job_name="Test Job"
    )
)
```