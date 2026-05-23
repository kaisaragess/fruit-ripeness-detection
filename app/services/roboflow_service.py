from flask import current_app
from inference_sdk import InferenceHTTPClient
import os

class RoboflowService:
    @staticmethod
    def run_detection(image_path):
        """
        Mengirim gambar ke Roboflow Workflow dan mengembalikan hasil analisis objek (buah rotten/fresh).
        """
        # Load config secara dinamis dari konteks aplikasi Flask yang sedang berjalan
        api_url = current_app.config.get("ROBOFLOW_API_URL")
        api_key = current_app.config.get("ROBOFLOW_API_KEY")
        workspace = current_app.config.get("ROBOFLOW_WORKSPACE")
        workflow_id = current_app.config.get("ROBOFLOW_WORKFLOW_ID")
        
        if not api_key:
            raise ValueError("Roboflow API Key is missing in configuration.")

        # Inisialisasi client
        client = InferenceHTTPClient(
            api_url=api_url,
            api_key=api_key
        )
        
        # Jalankan workflow
        result = client.run_workflow(
            workspace_name=workspace,
            workflow_id=workflow_id,
            images={
                "image": image_path
            },
            use_cache=True
        )
        
        if not result or len(result) == 0:
            raise RuntimeError("Roboflow returned an empty response.")
            
        # Ambil elemen pertama dari list output workflow
        output = result[0]
        
        # Mengembalikan dictionary output yang bersih
        return {
            "count_objects": output.get("count_objects", 0),
            "predictions": output.get("predictions", []),
            "annotated_image": output.get("output_image")  # base64 image string (bila ada di workflow)
        }
