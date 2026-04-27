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