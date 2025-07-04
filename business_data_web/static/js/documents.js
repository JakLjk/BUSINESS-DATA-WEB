const jobId = document.body.dataset.jobId
async function poll_documents_table() {
    try {
        const statusResponse = await fetch(`/documents-list-status/${jobId}`);
        const statusResult = await statusResponse.json();

        if (statusResult.status == 'finished') {
            const dataTableResponse = await fetch(`/documents-list-table/${jobId}`);
            const dataTableHTML = await dataTableResponse.text();
            document.getElementById("document-container").innerHTML = dataTableHTML;
            clearInterval(poolingInterval);
        }
        else if (statusResult.status == 'failed') {
            document.getElementById("status-message").innerHTML = 'Scraping job has failed';
            clearInterval(poolingInterval);
        }
        document.getElementById("status-message").innerHTML = `Status: ${statusResult.status}`;


    } catch (err) {
        console.error("Pooling error: ", err);
        document.getElementById("status-message").innerText = "Error communicating with API";
        clearInterval(poolingInterval);
    }
    
}
const poolingInterval = setInterval(poll_documents_table, 1000);