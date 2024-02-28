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
    let loadingInterval;
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

    // Function to reset the scan
    function resetScan() {
        timeoutIds.forEach(clearTimeout);
        statusElement.innerHTML = 'Scan stopped by user.';
        statusElement.classList.remove('alert-warning');
        statusElement.classList.add('alert-danger');
        updateProgress(0);
        scanning = false;
        scanButtonElement.innerText = 'Start';
    }

    // Function to perform the scan
    function performScan() {
        scanning = true;
        statusElement.innerHTML = 'Scanning...';
        statusElement.classList.remove('alert-info');
        statusElement.classList.add('alert-warning');

        let i = 0;
        loadingInterval = setInterval(function () {
            updateProgress(i);
            i += 10;
            if (i > 100) {
                clearInterval(loadingInterval);
                completeScan();
            }
        }, 1000);

        timeoutIds.push(loadingInterval);
    }

    // Function to add a domain to the allowed domains list
    function addDomainToAllowedList(domain) {
        // Retrieve the existing list of allowed domains from storage
        chrome.storage.local.get({ allowedDomains: [] }, function (result) {
            const allowedDomains = result.allowedDomains;
            // Add the new domain to the list if it doesn't already exist
            if (!allowedDomains.includes(domain)) {
                allowedDomains.push(domain);
                // Save the updated list back to storage
                chrome.storage.local.set({ allowedDomains: allowedDomains }, function () {
                    console.log('Domain added to allowed list:', domain);
                });
            } else {
                console.log('Domain already exists in the allowed list:', domain);
            }
        });
    }

    // Function to complete the scan
    function completeScan() {
        timeoutIds.forEach(clearTimeout);
        statusElement.innerHTML = 'Scan complete. Website is safe!';
        statusElement.classList.remove('alert-warning');
        statusElement.classList.add('alert-success');
        updateProgress(100);
    
        // Get the website link
        const websiteLink = websiteLinkElement.value;
    
        // Extract the domain from the website link
        const url = new URL(websiteLink);
        const domain = url.hostname;
    
        // Add the domain to the allowed domains list
        addDomainToAllowedList(domain);
    
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
    // populateWebsiteLink();
    // performScan();

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
                        performScan();
                    } else {
                        completeScan();
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
            performScan();
        }
    });
});
