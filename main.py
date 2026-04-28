import formlabs_local_api as formlabs
from formlabs_local_api import Manual, ManualLayerThicknessMm, SceneTypeModel, models
import pathlib
import sys
from mock_printers import MOCK_PRINTERS
from datetime import datetime
from log import write_log
from progressbar import ProgressBar, progressBarFromOperation
import argparse

def procedure():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preform-server-path", type=str, help="Path to PreFormServer executable")
    parser.add_argument("--stl-path", type=str, help="Path to STL folder", default=None)
    args = parser.parse_args()

    pathToPreformServer = None
    if args.preform_server_path:
        pathToPreformServer = pathlib.Path(args.preform_server_path)
    else:
        if sys.platform == 'win32':
            pathToPreformServer = pathlib.Path().resolve() / "PreFormServer/PreFormServer.exe"
        elif sys.platform == 'darwin':
            pathToPreformServer = pathlib.Path().resolve() / "PreFormServer.app/Contents/MacOS/PreFormServer"
        else:
            print("Unsupported platform")
            sys.exit(1)

    # Validate preform server path
    if not pathToPreformServer.exists():
        print("\nERROR: Unable to find a PreForm Server instance.")
        print(f"Tried path: {pathToPreformServer}")
        print('You can specify it manually with:')
        print('  --preform-server-path "/path/to/PreFormServer"\n')
        sys.exit(1)

    with formlabs.PreFormApi.start_preform_server(
        pathToPreformServer=pathToPreformServer
    ) as preform:
        # Create a stable file name based on datetime
        filename = datetime.now().strftime("%m-%d-%y_%H:%M:%S")

        # In the background, discover printers so the discovery process is over when we are ready to print
        preform.api.discover_devices(
            var_async=True,
            discover_devices_request=models.DiscoverDevicesRequest(
                timeout_seconds=60
            )
        )

        # Create scene
        print("Creating Scene")
        scene = preform.api.create_scene(SceneTypeModel(Manual(
            machine_type="FRML-4-0",
            material_code="FLPTB101",
            layer_thickness_mm=ManualLayerThicknessMm("0.05"),
            print_setting="DEFAULT",
        )))

        # Import teeth
        teeth_dir = pathlib.Path(args.stl_path) if args.stl_path else pathlib.Path().resolve() / "teeth"
        files = [f for f in teeth_dir.iterdir() if f.suffix.lower() == ".stl"]

        # Validate the teeth directory
        if not teeth_dir.exists() or not teeth_dir.is_dir():
          print("\nERROR: STL folder not found.")
          print(f"Tried path: {teeth_dir}")
          print('You can specify it manually with:')
          print('  --stl-path "/absolute/path/to/stl/folder"\n')
          sys.exit(1)

        import_pb = ProgressBar(total=len(files), prefix="Importing files: ", suffix="Complete")
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
                import_pb.update()

        # Auto orient
        auto_orient_operation = preform.api.auto_orient(
            scene_id=scene.id,
            var_async=True,
            auto_orient_request=models.AutoOrientRequest(
                models.DentalMode(
                    mode="DENTAL",
                    tilt=15
                )
            )
        )
        progressBarFromOperation(preform, "Auto-orienting:  ", auto_orient_operation.operation_id, 0.66)

        # Auto Support
        auto_support_operation = preform.api.auto_support(
            scene_id=scene.id,
            var_async=True,
            auto_support_request=models.AutoSupportRequest(
                density=0.85,
                touchpoint_size_mm=0.55,
                raft_type="MINI_RAFT"
            )
        )
        progressBarFromOperation(preform, "Auto-supporting: ", auto_support_operation.operation_id, 0.66)

        # Auto Layout
        auto_layout_operation = preform.api.auto_layout(
            scene_id=scene.id,
            var_async=True,
            auto_layout_request=models.AutoLayoutRequest(
                mode="DENTAL",
                lock_rotation=True
            )
        )
        progressBarFromOperation(preform, "Auto-layout:     ", auto_layout_operation.operation_id, 0.66)

        # Save file
        saving_operation = preform.api.save_form_file(
            scene_id=scene.id,
            var_async=True,
            load_form_file_request=models.LoadFormFileRequest(
                file=str(pathlib.Path().resolve() / (filename + "-B1.form"))
            )
        )
        progressBarFromOperation(preform, "Saving:          ", saving_operation.operation_id, 0.66)

        print("Loading connected devices")
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

        # Write a log to the log csv file
        write_log(filename + "-B1.form")

        # Upload a print to the printer
        preform.api.call_print(
            scene_id=scene.id,
            print_request=models.PrintRequest(
                printer=selected.ip_address,
                job_name="Test Job"
            )
        )

if __name__ == "__main__":
    procedure()
