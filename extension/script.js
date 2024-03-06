document.addEventListener('DOMContentLoaded', function () {
    // Check if necessary elements are present on the page
    const websiteLinkElement = document.getElementById('websiteLink');
    const loadingProgressElement = document.getElementById('loadingProgress');
    const statusElement = document.getElementById('status');
    const scanButtonElement = document.getElementById('scanButton');
    const containerElement = document.getElementById('container');

    if (!websiteLinkElement || !loadingProgressElement || !statusElement || !scanButtonElement || !containerElement) {
        console.error('One or more required elements not found. Exiting script.');
        return;
    }

    let scanning = false;
    let timeoutIds = [];

    // Function to populate the website link
    function populateWebsiteLink(callback) {
        chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
            if (tabs && tabs.length > 0) {
                websiteLinkElement.value = tabs[0].url;
                if (typeof callback === 'function') {
                    callback(); // Call the callback once the URL is populated
                }
            } else {
                console.error('Unable to get tab URL');
            }
        });
    }

    // Function to update the loading progress
    function updateProgress(percentage) {
        loadingProgressElement.style.width = percentage + '%';
    }

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

    // Function to reset the scan
    function resetScan() {
        abortScan();
        timeoutIds.forEach(clearTimeout);
        statusElement.innerHTML = 'Scan stopped by user.';
        statusElement.classList.remove('alert-warning');
        statusElement.classList.add('alert-danger');
        updateProgress(0);
        scanning = false;
        scanButtonElement.innerText = 'Start';
    }

    function performScan(domainToScan) {
        scanning = true;
        statusElement.innerHTML = 'Scanning...';
        statusElement.classList.remove('alert-info');
        statusElement.classList.add('alert-warning');
    
        let i = 0;
        const loadingInterval = setInterval(function () {
            updateProgress(i);
            i += 5;
            if (i > 100) {
                clearInterval(loadingInterval);
                console.log('Scan still in progress');
                // Handle the case where the backend is still processing
            }
        }, 1000);
    
        timeoutIds.push(loadingInterval);
    
        // Assuming scanEndpoint is the URL of your Flask /scan endpoint
        const scanEndpoint = 'http://127.0.0.1:5000/scan';
    
        // Fetch the data from the Flask API
        fetch(scanEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ domain: domainToScan }),
            timeout: 60000, // 60 seconds (adjust as needed)
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Clear the interval as soon as you receive data from the backend
                clearInterval(loadingInterval);
                console.log('Scan result:', data.scan_result);
                completeScan(data.scan_result);
            })
            .catch(error => {
                console.error('Error during scan:', error);
                clearInterval(loadingInterval);
                // Call abortScan in case of an error
                abortScan();
            });
    }
    

    // Function to add a domain to the allowed domains list
    function addDomainToAllowedList(domain) {
        // Retrieve the existing list of allowed domains from storage
        chrome.storage.local.get({ allowedDomains: [], unscannedDomains: [] }, function (result) {
            const allowedDomains = result.allowedDomains;
            const unscannedDomains = result.unscannedDomains;

            // Remove the domain from unscannedDomains if it exists
            const updatedUnscannedDomains = unscannedDomains.filter(unscannedDomain => unscannedDomain !== domain);

            // Add the new domain to the list if it doesn't already exist
            if (!allowedDomains.includes(domain)) {
                allowedDomains.push(domain);

                // Save the updated lists back to storage
                chrome.storage.local.set({
                    allowedDomains: allowedDomains,
                    unscannedDomains: updatedUnscannedDomains
                }, function () {
                    console.log('Domain added to allowed list:', domain);
                });
            }
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

    // Function to add a domain to the unscanned domains list
    function addDomainToUnscannedList(domain) {
        // Retrieve the existing lists of unscanned, allowed, and malicious domains from storage
        chrome.storage.local.get({unscannedDomains: [], allowedDomains: [], maliciousDomains: []}, function (result) {
            const unscannedDomains = result.unscannedDomains;
            const allowedDomains = result.allowedDomains;
            const maliciousDomains = result.maliciousDomains;

            // Check if the domain exists in allowedDomains or maliciousDomains
            const isInAllowedDomains = allowedDomains.includes(domain);
            const isInMaliciousDomains = maliciousDomains.includes(domain);

            // If the domain exists in allowedDomains, remove it
            if (isInAllowedDomains) {
                const updatedAllowedDomains = allowedDomains.filter(allowedDomain => allowedDomain !== domain);
                chrome.storage.local.set({ allowedDomains: updatedAllowedDomains });
            }

            // If the domain exists in maliciousDomains, remove it
            if (isInMaliciousDomains) {
                const updatedMaliciousDomains = maliciousDomains.filter(maliciousDomain => maliciousDomain !== domain);
                chrome.storage.local.set({ maliciousDomains: updatedMaliciousDomains });
            }

            // Add the new domain to the unscanned list if it doesn't already exist
            if (!unscannedDomains.includes(domain)) {
                unscannedDomains.push(domain);

                // Save the updated lists back to storage
                chrome.storage.local.set({
                    unscannedDomains: unscannedDomains,
                }, function () {
                    console.log('Domain added to unscanned list:', domain);
                });
            }
        });
    }


    // Function to complete the scan
    function completeScan(malicious_result) {
        timeoutIds.forEach(clearTimeout);
        console.log("This is result" + malicious_result);
        // Handle the data received from the backend as needed
        if (malicious_result === false) {
            statusElement.innerHTML = 'Safe';
            statusElement.classList.remove('alert-warning');
            statusElement.classList.add('alert-success');
            updateProgress(100);
        } else if (malicious_result == true) {
            statusElement.innerHTML = 'Malicious';
            statusElement.classList.remove('alert-warning');
            statusElement.classList.add('alert-danger');
            updateProgress(100);
        } else {
            statusElement.innerHTML = 'Scan stopped.';
            statusElement.classList.remove('alert-danger');
            statusElement.classList.add('alert-warning');
        }
        
    
        // Get the website link
        const websiteLink = websiteLinkElement.value;
    
        // Extract the domain from the website link
        const url = new URL(websiteLink);
        const domain = url.hostname;
    
        // Add the domain to the allowed domains list
        if (malicious_result == true){
            addDomainToAllowedList(domain);
        }else if (malicious_result == false){
            addDomainToMaliciousList(domain);
        }else{
            addDomainToUnscannedList(domain);
        }
        
    
        scanButtonElement.disabled = false;
        scanning = false;
        scanButtonElement.innerText = 'Start';
    }

        // Function to update the allowed domains list in the HTML
    function updateAllowedDomainsList(allowedDomains) {
        const allowedDomainsList = document.getElementById('allowedDomainsList');

        // Clear existing list items
        allowedDomainsList.innerHTML = '';

        // Populate the list with allowed domains
        allowedDomains.forEach(domain => {
            const listItem = document.createElement('li');
            listItem.textContent = domain;
            allowedDomainsList.appendChild(listItem);
        });
    }

    // Function to get and update the allowed domains list from storage
    function updateAllowedDomainsListFromStorage() {
        chrome.storage.local.get({ allowedDomains: [] }, function (result) {
            const allowedDomains = result.allowedDomains;
            updateAllowedDomainsList(allowedDomains);
        });
    }

    // Function to check if the domain is in allowedDomains or maliciousDomains
    function isDomainInLists(domain, allowedDomains, maliciousDomains) {
        return allowedDomains.includes(domain) || maliciousDomains.includes(domain);
    }

    // Populate the website link on extension popup open
    populateWebsiteLink(function () {
        // Check whether to run performScan outside the function
        const websiteLink = websiteLinkElement.value;
        if (websiteLink) {
            try {
                // Attempt to construct the URL from the input
                const url = new URL(websiteLink);
                const domainToCheck = url.hostname;

                chrome.storage.local.get({ allowedDomains: [], maliciousDomains: [] }, function (result) {
                    const allowedDomains = result.allowedDomains;
                    const maliciousDomains = result.maliciousDomains;

                    if (!isDomainInLists(domainToCheck, allowedDomains, maliciousDomains)) {
                        // If the domain is not in allowedDomains or maliciousDomains, run the scan
                        performScan(websiteLinkElement.value);
                    } else {
                        statusElement.innerHTML = 'Domain has been scanned!';
                        updateProgress(100);
                        scanButtonElement.disabled = false;
                        scanning = false;
                        scanButtonElement.innerText = 'Start';
                    }
                });
            } catch (error) {
                console.error('Invalid URL:', websiteLink);
                // Handle the error, e.g., show a message to the user
            }
        }
    });

    // "Start/Stop" button click event
    scanButtonElement.addEventListener('click', function () {
        if (scanning) {
            // If loading or scanning is in progress, confirm the stop
            if (confirm('Are you sure you want to stop the scan?')) {
                resetScan();
            }
        } else {
            // If not scanning, start the scan
            scanButtonElement.innerText = 'Stop';
            performScan(websiteLinkElement.value);
        }
    });
});
