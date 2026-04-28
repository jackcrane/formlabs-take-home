import formlabs_local_api as formlabs
from formlabs_local_api import Manual, ManualLayerThicknessMm, SceneTypeModel, models
import pathlib
import sys

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

        # print("Server running. Press ENTER to shut down...")
        # input()  # blocks here

if __name__ == "__main__":
    hello_server()