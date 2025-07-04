// GLOBALS
let waitingForDownloadHashIds = []
let downloadReadyNotified = false;


// MAIN POOLING LOOP
async function pollStatuses() {
    console.debug("Pooling statuses of documents")
    const unfinishedHashIds = [];
    document.querySelectorAll("tr[data-hash-id]")
        .forEach(row => {
            const hashId = row.getAttribute("data-hash-id");
            const statusCell = document.getElementById(`status-${hashId}`);
            if (statusCell && statusCell.innerText !== "finished") {
                unfinishedHashIds.push(hashId);
            }
        });

        if (unfinishedHashIds.length === 0) {
            clearInterval(pollingInterval);
            return;
        }        
    const statuses = await fetchStatuses(unfinishedHashIds);
    updateTableStatuses(statuses)

    // DOWNLOAD LOGIC
    if (waitingForDownloadHashIds.length > 0 &&  !downloadReadyNotified) {
        const allFinished = waitingForDownloadHashIds.every(hash_id => {
            const statusCell = document.getElementById(`status-${hash_id}`);
            return statusCell && statusCell.innerText.toLowerCase() === "finished";
        });
        if (allFinished){
            downloadReadyNotified = true;
            const popupDownload = document.getElementById("download-ready-popup");
            popupDownload.style.display ="block";
        }
    }
}

const pollingInterval = setInterval(pollStatuses, 3000);


// LOGIC FOR CHECKING CURRENT DOCUMENT STATUSES IN DB
async function fetchStatuses(hashIds) {
    try {
        const response = await fetch("/documents-scraping-status",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(hashIds)
            }
        );
        const result = await response.json();
        console.debug(result)
        return result
        
    }
    catch (err) {
        console.error("Error fetching statuses: ", error);
        return {};
    }
}

// LOGIC FOR UPDATING STATUSES IN THE TABLE DISPLAY
async function updateTableStatuses(statuses) {
    for (const [hashId, status] of Object.entries(statuses)) {
        const statusCell = document.getElementById(`status-${hashId}`);
        if (statusCell) {
            statusCell.innerText = status;
        }
    }
}


// LOGIC FOR STARTING DOWNLOAD PROCESS 
// IT SENDS REQUEST TO API TO GET ALL DOCUMENTS READY (I.E. TO FETCH THEM FROM CENTRAL REPO IF
// NOT AVIAILABLE IN LOCAL DB)
document.getElementById("document-container").addEventListener("click", async (event) => {
    if (event.target && event.target.id==="download-selected-btn") {
    const krsNumber = document.body.dataset.krsNumber;
    const selectedHashIds = Array.from(document.querySelectorAll(".download-checkbox:checked"))
                            .map(cb => cb.closest("tr").dataset.hashId);
    if (selectedHashIds.length === 0) {
        alert("No hash ids selected");
        return;
    }
    waitingForDownloadHashIds = selectedHashIds;
    downloadReadyNotified = false;
    try {
        const payload = {
            hashIds:selectedHashIds,
            krsNumber:krsNumber
        }
        const response = await fetch('/document-scrape', {
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify(payload)
        });
        if (!response.ok) {
            throw new Error(`Download error: ${response.status}`);
        }
    }
    catch (err) {
        console.error("Error has occurred while adding scrapign task: ", err);
        alert("Failed to start scraping session")
    }
}
});

// DOWNLOAD BUTTON 
// SHOWS WHEN POOLING LOOP DETECTS THAT ALL FILES ARE READY FOR DOWNLOAD
document.getElementById("download-now-btn").addEventListener("click", async () => {
    document.getElementById("download-ready-popup").style.display="None";
    try {
        console.info(waitingForDownloadHashIds);
        const input = document.getElementById("download-form-hash-ids");
        input.value = JSON.stringify(waitingForDownloadHashIds);
        document.getElementById("download-form").submit()

        // const payload = {waitingForDownloadHashIds}
        // console.info(payload)
        // const response = await fetch('/document-download', {
        //     method:"POST",
        //     headers:{"Content-Type":"application/json"},
        //     body:JSON.stringify(waitingForDownloadHashIds)
        // })

    }
    catch (err) {
        console.error("Error has occurred while adding scraping task: ", err)
        alert("Download function has failed")
    }

    

});
document.getElementById("download-close-btn").addEventListener("click", () => {
    document.getElementById("download-ready-popup").style.display="none";
});