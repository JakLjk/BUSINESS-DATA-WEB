import os
import requests
from dotenv import load_dotenv
from flask import Blueprint, render_template, request

load_dotenv()

root_bp = Blueprint('root', __name__)

@root_bp.route('/')
def index():
    return render_template('index.html')

@root_bp.route("/documents", methods=["POST"])
def documents():
    krs_number:str = request.form.get("krs_number")
    get_krsdf_docs_url = (
                            os.getenv("API_BASE_URL")
                            +
                            os.getenv("API_ROUTE_KRSDF")
                            +
                            os.getenv("API_KRSDF_GET_DOCUMENT_NAMES")
                        )
    result_data = ""
    try:
        response = requests.get(f"{get_krsdf_docs_url}?krs={krs_number}")
        response.raise_for_status()
        data = response.json()
        result_url = data["data"]
        result_response = requests.get(result_url)
        result_response.raise_for_status()
        result_data = result_response.json()
    except requests.RequestException as e:
        print(f"API request failed: {e}")

    return result_data
    

