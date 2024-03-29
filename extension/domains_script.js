document.addEventListener("DOMContentLoaded", function () {
    // DOM elements
    var unscannedDomainsList = document.getElementById("unscannedDomainsList");
    var allowedDomainsList = document.getElementById("allowedDomainsList");
    var maliciousDomainsList = document.getElementById("maliciousDomainsList");
    var historyToggle = document.getElementById("historyToggle");
    var scanAllButton = document.getElementById("scanAllButton");
    var tabs = document.querySelectorAll('.tab');
    var tabContents = document.querySelectorAll('.tab-content');
    var removeAllButton = document.getElementById("removeAllButton");
    // Select the loading modal
    var loadingModal = document.getElementById('loadingModal');

    var scanningInProgress = false;

    // Check if necessary elements are present
    if (!unscannedDomainsList || !allowedDomainsList || !maliciousDomainsList || !historyToggle || !scanAllButton) {
        console.error("Elements not found.");
        return;
    }

    chrome.storage.local.get(null, function(result) {
        console.log('Contents of chrome.storage.local:', result);
    });

    chrome.storage.local.get(['historyEnabled'], function(result) {
        historyToggle.checked = result.historyEnabled ?? true;
        if (historyToggle.checked == true){
            getUniqueDomainsFromHistory(function(domainSet) {
                // Do something with domainSet here
                console.log(domainSet);
                // Initialize the extension on page load
                chrome.storage.local.get(['unscannedDomains', 'allowedDomains', 'maliciousDomains'], function (result) {
                    populateDomainList(allowedDomainsList, result.allowedDomains);
                    populateDomainList(maliciousDomainsList, result.maliciousDomains);
                    populateDomainList(unscannedDomainsList, result.unscannedDomains);
                });
            });
        }else{
            chrome.storage.local.get(['unscannedDomains', 'allowedDomains', 'maliciousDomains'], function (result) {
                populateDomainList(allowedDomainsList, result.allowedDomains);
                populateDomainList(maliciousDomainsList, result.maliciousDomains);
                populateDomainList(unscannedDomainsList, result.unscannedDomains);
            });
        }
    });

    // Event listener for tab switching
    tabs.forEach(function (tab) {
        tab.addEventListener('click', function () {
            var tabName = this.getAttribute('data-tab');
            switchTab(tabName);
        });
    });

    // Function to switch tab content visibility
    function switchTab(tabName) {
        tabs.forEach(function (tab) {
            tab.classList.remove('active');
        });

        tabContents.forEach(function (tabContent) {
            tabContent.classList.remove('active');
        });

        var activeTab = document.querySelector('.tab[data-tab="' + tabName + '"]');
        var activeTabContent = document.getElementById(tabName + 'Content');

        activeTab.classList.add('active');
        activeTabContent.classList.add('active');
    }

    // Function to check if domain is already in the list
    function isDomainInList(list, domain) {
        var domainItems = list.querySelectorAll('.domain-item span');
        return Array.from(domainItems).some(item => item.textContent === domain);
    }

    // Function to populate domain list, avoiding duplicates
    function populateDomainList(list, domains) {
        if (domains != undefined){
            // Iterate over each element and call populateDomainList
            for (let i = 0; i < domains.length; i++) {
                if (!isDomainInList(list, domains[i])) {
                    var newDomainItem = document.createElement("div");
                    newDomainItem.className = "domain-item";
                    newDomainItem.innerHTML = '<span>' + domains[i] + '</span>' +
                        '<div class="btn-group">' +
                        '<button class="btn btn-sm btn-danger remove-btn">Remove</button>' +
                        '<button class="btn btn-sm btn-primary scan-btn">Scan</button>' +
                        '</div>';
                    list.appendChild(newDomainItem);
                }
            }
        }
        
    }

    // Event listener for history toggle button
    historyToggle.addEventListener("change", function () {
        if (confirm("Changing this setting may affect your domain list. Are you sure you want to proceed?")) {
            // get history based on toggle state
            if (historyToggle.checked) {
                getUniqueDomainsFromHistory();
                window.location.reload();
            } else {
                console.log("Reading history is disabled.");
            }
            chrome.storage.local.set({ historyEnabled: historyToggle.checked });
        } else {
            historyToggle.checked = !historyToggle.checked;
        }
    });

    // Event listener for the "Remove All Domains" button
    removeAllButton.addEventListener("click", function () {
        if (confirm("Are you sure you want to remove all domains?")) {
            clearDomainList(unscannedDomainsList);
            clearDomainList(allowedDomainsList);
            clearDomainList(maliciousDomainsList);

            // Clear domains from storage
            chrome.storage.local.set({
                unscannedDomains: [],
                allowedDomains: [],
                maliciousDomains: []
            });
        }
    });

    // Event listener to remove domain
    [unscannedDomainsList, allowedDomainsList, maliciousDomainsList].forEach(list => {
        list.addEventListener("click", function (event) {
            var removeButton = event.target.closest('.remove-btn');
            var scanButton = event.target.closest('.scan-btn');

            if (removeButton) {
                var domainItem = removeButton.closest('.domain-item');
                var removedDomainText = domainItem.querySelector('span').textContent;
                // remove domain 
                if (confirm("Are you sure you want to remove domain '" + removedDomainText + "'?")) {
                    removeButton.closest('.domain-item').remove();
                    console.log("Domain removed successfully");
                    updateStorageAfterRemoval(removedDomainText);
                }
            } else if (scanButton) {
                // scan domain
                var domainItem = scanButton.closest('.domain-item');
                var scannedDomainText = domainItem.querySelector('span').textContent;
                if (confirm("Are you sure you want to scan domain '" + scannedDomainText + "'?")) {
                    // Show the loading modal
                    loadingModal.style.display = 'block';

                    var scanStatus = document.getElementById("scan_status");
                    var scanningMessage = document.getElementById("scanningMessage");
                    var spinner = document.querySelector('.spinner-border');
                    // Call scanDomains, which returns a promise
                    scanDomains(scannedDomainText)
                    .then(domain_result => {
                        console.log(domain_result);
                        if (domain_result != null) {
                            // scanStatus.textContent = 'Scan Completed';
                            var resultText = domain_result ? 'Malicious' : 'Safe';
                            scanningMessage.textContent = scannedDomainText + " [" + resultText + "]";
                            completeScan({ [scannedDomainText]: domain_result});
                            downloadReport(scannedDomainText, scanningMessage)
                        } else {
                            scanStatus.textContent = 'Scan Failed';
                            scanningMessage.textContent = "Failed to scan domain: " + scannedDomainText;
                        }
                        // Hide the spinner
                        spinner.style.display = 'none';
                    })
                    .catch(error => {
                        // console.error('Error:', error);
                        // Handle the error, such as showing an error message
                        // Check if the spinner element exists
                        scanStatus.textContent = 'Scan Failed';
                        scanningMessage.textContent = "Failed to scan domain: " + scannedDomainText;
                    });
                }
            }
        });
    });

    function completeScan(domainResults) {
        console.log("Complete scan results:", domainResults);
        (async () => {
            for (const [domain, result] of Object.entries(domainResults)) {
                if (!Boolean(result)) {
                    await addDomainToAllowedList(domain);
                } else {
                    addDomainToMaliciousList(domain);
                }
            }
        })();
    }
    

    // Function to add a domain to the allowed domains list
    function addDomainToAllowedList(domain) {
        console.log(domain);
        return new Promise((resolve, reject) => {
            // Retrieve the existing list of allowed domains from storage
            chrome.storage.local.get({ allowedDomains: [], unscannedDomains: [] }, function (result) {
                const allowedDomains = result.allowedDomains;
                const unscannedDomains = result.unscannedDomains;

                // Remove the domain from unscannedDomains if it exists
                const updatedUnscannedDomains = unscannedDomains.filter(unscannedDomain => unscannedDomain !== domain);

                // Add the new domain to the list if it doesn't already exist
                if (!allowedDomains.includes(domain)) {
                    allowedDomains.push(domain);
                    console.log(allowedDomains);
                    // Save the updated lists back to storage
                    chrome.storage.local.set({
                        allowedDomains: allowedDomains,
                        unscannedDomains: updatedUnscannedDomains
                    }, function () {
                        console.log('Domain added to allowed list:', domain);
                        resolve(); // Resolve the promise once the storage operation is completed
                    });
                } else {
                    resolve(); // Resolve the promise if the domain already exists
                }
            });
        });
    }


    // Function to add a domain to the malicious domains list
    function addDomainToMaliciousList(domain) {
        // Retrieve the existing list of malicious domains from storage
        chrome.storage.local.get({ maliciousDomains: [], unscannedDomains: [] }, function (result) {
            const maliciousDomains = result.maliciousDomains;
            const unscannedDomains = result.unscannedDomains;

            // Remove the domain from unscannedDomains if it exists
            const updatedUnscannedDomains = unscannedDomains.filter(unscannedDomain => unscannedDomain !== domain);

            // Add the new domain to the list if it doesn't already exist
            if (!maliciousDomains.includes(domain)) {
                maliciousDomains.push(domain);

                // Save the updated lists back to storage
                chrome.storage.local.set({
                    maliciousDomains: maliciousDomains,
                    unscannedDomains: updatedUnscannedDomains
                }, function () {
                    console.log('Domain added to malicious list:', domain);
                });
            }
        });
    }

    // Function to clear domain list
    function clearDomainList(list) {
        while (list.firstChild) {
            list.removeChild(list.firstChild);
        }
        console.log("Domains list cleared.");
    }

    // Function to update storage after domain removal
    function updateStorageAfterRemoval(removedDomain) {
        chrome.storage.local.get(['unscannedDomains', 'allowedDomains', 'maliciousDomains'], function (result) {
            const updatedunscannedDomains = (result.unscannedDomains ?? []).filter(d => d !== removedDomain);
            const updatedAllowedDomains = (result.allowedDomains ?? []).filter(d => d !== removedDomain);
            const updatedMaliciousDomains = (result.maliciousDomains ?? []).filter(d => d !== removedDomain);

            chrome.storage.local.set({
                unscannedDomains: updatedunscannedDomains,
                allowedDomains: updatedAllowedDomains,
                maliciousDomains: updatedMaliciousDomains
            });
        });
    }

    function scanDomains(data) {
        if (Array.isArray(data)) {
            scanningInProgress = true;
            // It's an array, call scan-all API
            return fetch('http://127.0.0.1:5000/scan-all', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ domains: data }),
            })
            .then(response => response.json())
            .then(result => {
                scanningInProgress = false;
                return result.results;
            })
            .catch(error => {
                console.error('Error:', error);
                scanningInProgress = false;
                return null;
            });
        } else if (typeof data === 'string') {
            scanningInProgress = true;
            // It's a string, call scan API
            return fetch('http://127.0.0.1:5000/scan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ link: data }),
            })
            .then(response => response.json())
            .then(result => {
                console.log(result.results);
                scanningInProgress = false;
                return result.results;
            })
            .catch(error => {
                console.error('Error:', error);
                scanningInProgress = false;
                return null;
            });
        } else {
            console.error('Invalid input type');
            // Handle invalid input type
            scanningInProgress = false;
            return null;
        }
    }
    

    // Event listener for the scan button
    scanAllButton.addEventListener("click", function () {
        // Show the loading modal
        loadingModal.style.display = 'block';

        // Get the list of unscanned domains
        const unscannedDomains = Array.from(document.querySelectorAll('#unscannedDomainsList .domain-item span'))
                                    .map(item => item.textContent);

        const spinner = document.querySelector('.spinner-border');
        const scanStatus = document.getElementById("scan_status");
        const scanningMessage = document.getElementById("scanningMessage");

        scanDomains(unscannedDomains)
        .then(domain_result => {
            console.log(domain_result);

            var message = '';
            const domainResults = {}; // Initialize an empty object to store domain results
            // Loop through the results and concatenate into the message
            for (const [domain, result] of Object.entries(domain_result)) {
                const resultText = result ? 'Malicious' : 'Safe';
                message += `${domain} [${resultText}] <br/>`;
                domainResults[domain] = result; // Store the result in the dictionary
            }
            completeScan(domainResults);
            scanStatus.textContent = "Scan Completed";
            scanningMessage.innerHTML = message;
            // Hide the spinner
            spinner.style.display = 'none';


        })
        .catch(error => {
            console.error(error);
            scanStatus.textContent = 'Scan Failed';
            scanningMessage.textContent = "Failed to scan all domains";
            // Hide the spinner
            spinner.style.display = 'none';
        });
    });

    // Function to send an abort signal to the server
    function abortScan() {
        fetch('http://127.0.0.1:5000/abort-scan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({}),
        }).then(response => {
            if (response.ok) {
                console.log('Abort signal sent successfully');
            } else {
                console.error('Failed to send abort signal');
            }
        }).catch(error => {
            console.error('Error sending abort signal:', error);
        });
    }

    // Get the close button element
    var closeButton = document.querySelector('#loadingModal .close');

    // Add an event listener to the close button
    if (closeButton) {
        closeButton.addEventListener('click', function() {
            // Check if the modal exists and is a Bootstrap modal
            loadingModal.style.display = 'none';
            if (scanningInProgress){
                abortScan();
            }else{
                window.location.reload();
            }
            
        });
    }

    function getUniqueDomainsFromHistory(callback) {
        const microsecondsPerWeek = 1000 * 60 * 60 * 24 * 7;
        const oneWeekAgo = (new Date()).getTime() - microsecondsPerWeek;
    
        chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
            if (tabs && tabs.length > 0) {
                // const currentDomain = new URL(tabs[0].url).hostname;
    
                chrome.history.search({
                    'text': '',
                    'startTime': oneWeekAgo
                }, function (historyItems) {
                    chrome.storage.local.get({ allowedDomains: [], maliciousDomains: [] }, function (result) {
                        const allowedDomains = result.allowedDomains;
                        const maliciousDomains = result.maliciousDomains;
                        
                        const domainSet = [...new Set(historyItems
                            .map(item => new URL(item.url).hostname)
                            .filter(domain => !allowedDomains.includes(domain) && !maliciousDomains.includes(domain)))];

                        chrome.storage.local.set({ unscannedDomains: Array.from(domainSet) });
    
                        if (typeof callback === 'function') {
                            callback(domainSet);
                        }
                    });
                });
            } else {
                console.error('Unable to get current tab information');
            }
        });
    }
    
    function downloadReport(domainToDownload, statusElement){
        // Create a download button
        const downloadButton = document.createElement('button');
        downloadButton.textContent = 'Download Report';
        downloadButton.classList.add('btn', 'btn-primary');
        downloadButton.onclick = function() {
            // Functionality to download the report
            // Replace this with your actual download logic
            console.log('Download report clicked');

            const downloadEndpoint = 'http://127.0.0.1:5000/download';
            fetch(downloadEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({domain: domainToDownload}),
            })
            .then(response =>{
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data =>{
                pdfData = data.pdf_base64;
                // Decode the base64 string to binary data
                const binaryData = atob(pdfData);
                const arrayBuffer = new ArrayBuffer(binaryData.length);
                const uint8Array = new Uint8Array(arrayBuffer);
                for (let i = 0; i < binaryData.length; i++) {
                    uint8Array[i] = binaryData.charCodeAt(i);
                }

                // Create a Blob from the binary data
                const blob = new Blob([uint8Array], { type: 'application/pdf' });

                // Create a download link
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = domainToDownload + '_report.pdf'; // Set the filename for the download
                document.body.appendChild(a);
                a.click();

                // Clean up
                window.URL.revokeObjectURL(url);
            })
            .catch(error =>{
                console.error('Error during download:', error);
            })
        };

        // Append the download button to the status element
        statusElement.appendChild(downloadButton);

        // Float the button to the right
        downloadButton.style.float = 'right';
        // Make the button smaller
        downloadButton.classList.add('btn-sm');
    }

});



// Add an event listener for the 'unload' event
window.addEventListener('unload', function(event) {
    // Perform actions when the plugin screen is closed
    console.log('Plugin screen is closed');
    // You can perform additional actions here
    abortScan();
});