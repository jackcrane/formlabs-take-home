import formlabs_local_api as formlabs
from formlabs_local_api import Manual, ManualLayerThicknessMm, SceneTypeModel, models
import pathlib
import sys
from mock_printers import MOCK_PRINTERS

def hello_server():
    pathToPreformServer = None
    if sys.platform == 'win32':
        pathToPreformServer = pathlib.Path().resolve() / "PreFormServer/PreFormServer.exe"
    elif sys.platform == 'darwin':
        pathToPreformServer = pathlib.Path().resolve() / "PreFormServer.app/Contents/MacOS/PreFormServer"
    else:
        print("Unsupported platform")
        sys.exit(1)

    with formlabs.PreFormApi.start_preform_server(
        pathToPreformServer=pathToPreformServer
    ) as preform:
        # In the background, discover printers so the discovery process is over when we are ready to print
        preform.api.discover_devices(
            var_async=True,
            discover_devices_request=models.DiscoverDevicesRequest(
                timeout_seconds=60
            )
        )

        # Create scene
        scene = preform.api.create_scene(SceneTypeModel(Manual(
            machine_type="FRML-4-0",
            material_code="FLPTB101",
            layer_thickness_mm=ManualLayerThicknessMm("0.05"),
            print_setting="DEFAULT",
        )))

        # Import teeth
        teeth_dir = pathlib.Path().resolve() / "teeth"

        for file in teeth_dir.iterdir():
            if file.suffix.lower() == ".stl":
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

        # Auto orient
        preform.api.auto_orient(
            scene_id=scene.id,
            auto_orient_request=models.AutoOrientRequest(
                models.DentalMode(
                    mode="DENTAL",
                    tilt=15
                )
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

        # Screenshot workspace
        preform.api.save_screenshot(
            scene_id = scene.id,
            save_screenshot_request=models.SaveScreenshotRequest(
                file=str(pathlib.Path().resolve() / "image.png"),
            )
        )

        # Save file for sanity checking
        preform.api.save_form_file(
            scene_id=scene.id,
            load_form_file_request=models.LoadFormFileRequest(
                file=str(pathlib.Path().resolve() / "plate.form")
            )
        )

        # Get devices
        printers = preform.api.get_devices(
            can_print=True,
        )

        if printers.count == 0:
          print("No available printers.")
          choice = input("Press 'm' to load mock printers or any other key to exit: ").strip().lower()
          if choice != "m":
              return
          print("You are using mock printer data. This will allow you to pick from a list of fake printers. This will call the print API call to fail.")
          printers = MOCK_PRINTERS

        # Display options
        print("\nAvailable printers:")
        for i, p in enumerate(printers.devices):
            print(f"[{i}] {p.product_name} | {p.status} | {p.ip_address}")

        # Selection loop
        selected = None
        while selected is None:
            try:
                choice = int(input("Select printer index: ").strip())
                if 0 <= choice < len(printers.devices):
                    selected = printers.devices[choice]
                else:
                    print("Invalid index.")
            except ValueError:
                print("Enter a number.")

        # Upload a print to the printer
        preform.api.call_print(
            scene_id=scene.id,
            print_request=models.PrintRequest(
                printer=selected.ip_address,
                job_name="Test Job"
            )
        )


if __name__ == "__main__":
    hello_server()