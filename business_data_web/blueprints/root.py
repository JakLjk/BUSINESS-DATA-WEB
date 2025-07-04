import os
import json
import requests
from dotenv import load_dotenv
from flask import Response, Blueprint, render_template, request, stream_with_context

load_dotenv()

root_bp = Blueprint('root', __name__)

url_get_krsd_df_docs_list = (
         os.getenv("API_BASE_URL")
         +
         os.getenv("API_ROUTE_KRSDF")
         +
         os.getenv("API_KRSDF_GET_DOCUMENT_NAMES_RESULT")
    )
url_get_krsd_df_docs__scraping_statuses = (
        os.getenv("API_BASE_URL")
        +
        os.getenv("API_ROUTE_KRSDF")
        +
        os.getenv("API_KRSDF_DOCUMENTS_SCRAPING_STATUS")
    )

url_get_krsd_df_docs__scrape_documents = (
        os.getenv("API_BASE_URL")
        +
        os.getenv("API_ROUTE_KRSDF")
        +
        os.getenv("API_KRSDF_SCRAPE_DOCUMENTS")
    )

url_get_krsd_df_docs_download_documents = (
        os.getenv("API_BASE_URL")
        +
        os.getenv("API_ROUTE_KRSDF")
        +
        os.getenv("API_KRSDF_DOWNLOAD_DOCUMENTS")
    )

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
    try:
        response = requests.get(f"{get_krsdf_docs_url}/{krs_number}")
        response.raise_for_status()
        data = response.json()
        job_id = data["data"]["job_id"]
    except requests.RequestException as e:
        raise e
    return render_template("krsdf_documents_preview.html", krs_number=krs_number, job_id=job_id)

@root_bp.route("/documents-list-status/<job_id>", methods=["GET"])
def documents_list_status(job_id):
    get_krsd_ds_docs_list_url = (
         os.getenv("API_BASE_URL")
         +
         os.getenv("API_ROUTE_KRSDF")
         +
         os.getenv("API_KRSDF_GET_DOCUMENT_NAMES_RESULT")
         +
         f"/{job_id}"
    )
    try:
        response = requests.get(get_krsd_ds_docs_list_url)
        response.raise_for_status()
        data = response.json()
        status = data["status"]
    except requests.RequestException as e:
        raise e
    return {'status':status}

@root_bp.route("/documents-list-table/<job_id>", methods=["GET"])
def documents_list_table(job_id):

    try:
        response = requests.get(f"{url_get_krsd_df_docs_list}/{job_id}")
        response.raise_for_status()
        data = response.json()
        table = data["data"]
    except requests.RequestException as e:
        raise e

    return render_template("krsdf_documents_table.html", table=table)

@root_bp.route("/documents-scraping-status", methods=["POST"])
def documents_scraping_status():
    hash_ids = request.get_json()
    # print("--------------")
    # print(hash_ids)
    if not isinstance(hash_ids, list):
        return {"error":"expected list of hash ids"}, 400
    try:
        response = requests.post(
            url_get_krsd_df_docs__scraping_statuses,
            json=hash_ids
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        raise e
    if not data["status"] == "finished":
        raise Exception("Invalid data format")
    # print(data["data"])
    return data["data"]


    
@root_bp.route("/document-scrape", methods=["POST"])
def document_scrape():
    data = request.get_json()
    hash_ids = data["hashIds"]
    krs_number = data["krsNumber"]
    if not isinstance(hash_ids, list):
        return {"error":"expected list of hash ids"}, 400
    try:
        response = requests.post(
            f"{url_get_krsd_df_docs__scrape_documents}?krs={krs_number}",
            json=hash_ids
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        raise e
    return {"message":"Scraping task added to queue"}, 200


@root_bp.route("/document-download", methods=["POST"])
def document_download():
    hash_ids_raw = request.form.get("hash_ids")
    hash_ids = json.loads(hash_ids_raw)
    # print("xxxxxxxxxxxxxx")
    # print(hash_ids)
    if not isinstance(hash_ids, list):
        print("XXX")
        return {"error":"expected list of hash ids"}, 400
    try:
        response = requests.post(
            url_get_krsd_df_docs_download_documents,
            json=hash_ids,
            stream=True
        )
        response.raise_for_status()
        return Response(
            stream_with_context(response.iter_content(chunk_size=8192)),
            content_type="application/zip",
            headers={
                "Content-Disposition":"attachment; filename=documents.zip"
            }
        )

    except requests.RequestException as e:
        raise e



# TODO downlaod button should actually send a download request to krs df
# After all selected documents have finished downloading, popup should appear
# stating that download is ready (and this should download the files)
# TODO in fastapi add pending status
# TODO change exceptions into proper erro handling with returning error json
# TODO add some bloat to first parse and check the responses from the API, and not just pass them directly into jinja
