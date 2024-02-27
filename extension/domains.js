document.addEventListener("DOMContentLoaded", function () {
    // DOM elements
    var allowedDomainsList = document.getElementById("allowedDomainsList");
    var historyToggle = document.getElementById("historyToggle");
    var scanButton = document.getElementById("scanButton");

    // Check if necessary elements are present
    if (!allowedDomainsList || !historyToggle || !scanButton) {
        console.error("Elements not found.");
        return;
    }

    // Initialize the extension on page load
    chrome.storage.local.get(['historyEnabled', 'allowedDomains', 'scannedDomains'], function (result) {
        historyToggle.checked = result.historyEnabled ?? true;
        (result.allowedDomains ?? []).forEach(domain => appendDomainToList(domain, result.scannedDomains?.[domain]?.status));
        conditionalGetHistory();
    });

    // Function to append domain to the list
    function appendDomainToList(domain, scannedStatus) {
        if (!isDomainInList(domain)) {
            var newDomainItem = document.createElement("div");
            newDomainItem.className = "domain-item";
            newDomainItem.innerHTML = '<span>' + domain + '</span>' +
                '<span class="scanned-status">' + (scannedStatus || 'Not scanned') + '</span>' +
                '<button class="remove-btn">X</button>';
            allowedDomainsList.appendChild(newDomainItem);
        }
    }

    // Event listener for history toggle button
    historyToggle.addEventListener("change", function () {
        if (confirm("Changing this setting may affect your domain list. Are you sure you want to proceed?")) {
            // get history based on toggle state
            if (historyToggle.checked) {
                getUniqueDomainsFromHistory();
            } else {
                console.log("Reading history is disabled.");
                // clear domain list
                clearDomainsList();
                chrome.storage.local.set({ allowedDomains: [] });
            }
            chrome.storage.local.set({ historyEnabled: historyToggle.checked });
        } else {
            historyToggle.checked = !historyToggle.checked;
        }
    });

    // Event listener to remove domain
    allowedDomainsList.addEventListener("click", function (event) {
        var removeButton = event.target.closest('.remove-btn');
        if (removeButton) {
            var domainItem = removeButton.closest('.domain-item');
            var removedDomainText = domainItem.querySelector('span').textContent;
            // remove domain 
            if (confirm("Are you sure you want to remove domain '" + removedDomainText + "'?")) {
                removeButton.closest('.domain-item').remove();
                console.log("Domain removed successfully");
                updateStorageAfterRemoval(removedDomainText);
            }
        }
    });

    // Function to check if domain is already in the list
    function isDomainInList(domain) {
        var domainItems = allowedDomainsList.querySelectorAll('.domain-item span');
        return Array.from(domainItems).some(item => item.textContent === domain);
    }

    // Function to clear domains list
    function clearDomainsList() {
        while (allowedDomainsList.firstChild) {
            allowedDomainsList.removeChild(allowedDomainsList.firstChild);
        }
        console.log("Domains list cleared.");
    }

    // Function to update storage after domain removal
    function updateStorageAfterRemoval(removedDomain) {
        chrome.storage.local.get(['allowedDomains', 'scannedDomains'], function (result) {
            const updatedDomains = (result.allowedDomains ?? []).filter(d => d !== removedDomain);
            const updatedScannedStatus = { ...result.scannedDomains };
            delete updatedScannedStatus[removedDomain];

            chrome.storage.local.set({ allowedDomains: updatedDomains, scannedDomains: updatedScannedStatus });
        });
    }

    // Event listener for the scan button
    scanButton.addEventListener("click", function () {
        if (historyToggle.checked) {
            const domainItems = allowedDomainsList.querySelectorAll('.domain-item span');
            alert("Scanning all domains!");
        } else {
            alert("No domain to be scanned!");
        }
    });

    // Function to get unique domains from history
    function getUniqueDomainsFromHistory() {
        const microsecondsPerWeek = 1000 * 60 * 60 * 24 * 7;
        const oneWeekAgo = (new Date()).getTime() - microsecondsPerWeek;

        chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
            if (tabs && tabs.length > 0) {
                const currentDomain = new URL(tabs[0].url).hostname;

                chrome.history.search({
                    'text': '',
                    'startTime': oneWeekAgo
                }, function (historyItems) {
                    const domainSet = new Set(historyItems.map(item => new URL(item.url).hostname));
                    domainSet.delete(currentDomain);

                    domainSet.forEach(domain => {
                        appendDomainToList(domain);
                    });

                    chrome.storage.local.set({ allowedDomains: Array.from(domainSet) });
                });
            } else {
                console.error('Unable to get current tab information');
            }
        });
    }
});