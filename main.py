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

    # api = formlabs.PreFormApi()

    with formlabs.PreFormApi.start_preform_server(
        pathToPreformServer=pathToPreformServer
    ) as preform:
        scene = preform.api.create_scene(SceneTypeModel(Manual(
            machine_type="FRML-4-0",
            material_code="FLPTB101",
            layer_thickness_mm=ManualLayerThicknessMm("0.05"),
            print_setting="DEFAULT",
        )))

        preform.api.import_model(
            scene_id = scene.id,
            import_model_request=models.ImportModelRequest(
                file=str(pathlib.Path().resolve() / "benchy.stl")
            )
        )

        preform.api.save_screenshot(
            scene_id = scene.id,
            save_screenshot_request=models.SaveScreenshotRequest(
                file=str(pathlib.Path().resolve() / "image.png")
            )
        )

        print("Server running. Press ENTER to shut down...")
        input()  # blocks here

if __name__ == "__main__":
    hello_server()