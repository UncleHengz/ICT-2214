document.addEventListener("DOMContentLoaded", function () {
    var allowedDomainsList = document.getElementById("allowedDomainsList");
    var historyToggle = document.getElementById("historyToggle"); // Access the toggle button
    var scanButton = document.getElementById("scanButton");

    // Checks if buttons exist
    if (!allowedDomainsList || !historyToggle || !scanButton) {
        console.error("Elements not found.");
        return;
    }

    // Load saved settings and domains
    chrome.storage.local.get(['historyEnabled', 'allowedDomains'], function (result) {
        historyToggle.checked = result.historyEnabled ?? true; // Default to true if undefined
        (result.allowedDomains ?? []).forEach(domain => appendDomainToList(domain));
        conditionalGetHistory(); // Adjust based on the loaded toggle state
    });

    // Checks if history is toggled
    function conditionalGetHistory() {
        if (historyToggle.checked) {
            getUniqueDomainsFromHistory();
        } else {
            console.log("Reading history is disabled.");
            clearDomainsList(); // Call to clear the domains list if toggled off
        }
    }

    // Event listener for history toggle button
    historyToggle.addEventListener("change", function () {
        if (confirm("Changing this setting may affect your domain list. Are you sure you want to proceed?")) {
            conditionalGetHistory();
            // Save the toggle state to storage
            chrome.storage.local.set({ historyEnabled: historyToggle.checked });
        } else {
            // If the user cancels, revert the toggle state
            historyToggle.checked = !historyToggle.checked;
        }
    });

    // Clear all entries in domain list
    function clearDomainsList() {
        while (allowedDomainsList.firstChild) {
            allowedDomainsList.removeChild(allowedDomainsList.firstChild);
        }
        console.log("Domains list cleared.");
        // Also clear the saved domains if history is disabled
        if (!historyToggle.checked) {
            chrome.storage.local.set({ allowedDomains: [] });
        }
    }

    // Event listener to remove domain
    allowedDomainsList.addEventListener("click", function (event) {
        var removeButton = event.target.closest('.remove-btn');
        if (removeButton) {
            var domainItem = removeButton.closest('.domain-item');
            var removedDomainText = domainItem.querySelector('span').textContent;
            if (confirm("Are you sure you want to remove domain '" + removedDomainText + "'?")) {
                removeDomain(removeButton, removedDomainText);
            }
        }
    });

    // Function to remove domain 
    function removeDomain(button, domain) {
        button.closest('.domain-item').remove();
        console.log("Domain removed successfully");
        // Update the list in storage after removal
        updateStorageAfterRemoval(domain);
    }

    // Function to update the chrome storage after removal
    function updateStorageAfterRemoval(removedDomain) {
        chrome.storage.local.get(['allowedDomains'], function (result) {
            const updatedDomains = (result.allowedDomains ?? []).filter(d => d !== removedDomain);
            chrome.storage.local.set({ allowedDomains: updatedDomains });
        });
    }

    // checks if domain is already in the list
    function isDomainInList(domain) {
        var domainItems = allowedDomainsList.querySelectorAll('.domain-item span');
        return Array.from(domainItems).some(item => item.textContent === domain);
    }

    // Adds domain to the list
    function appendDomainToList(domain) {
        if (!isDomainInList(domain)) {
            var newDomainItem = document.createElement("div");
            newDomainItem.className = "domain-item";
            newDomainItem.innerHTML = '<span>' + domain + '</span><button class="remove-btn">X</button>';
            allowedDomainsList.appendChild(newDomainItem);
        }
    }

    // Retrieve domains from user's history
    function getUniqueDomainsFromHistory() {
        const microsecondsPerWeek = 1000 * 60 * 60 * 24 * 7; // past 7 days
        const oneWeekAgo = (new Date()).getTime() - microsecondsPerWeek;

        chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
            if (tabs && tabs.length > 0) {
                const currentDomain = new URL(tabs[0].url).hostname;

                chrome.history.search({
                    'text': '', // Search string is empty to get all history items
                    'startTime': oneWeekAgo
                }, function (historyItems) {
                    const domainSet = new Set(historyItems.map(item => new URL(item.url).hostname));

                    // Remove the current page's domain from the set
                    domainSet.delete(currentDomain);

                    domainSet.forEach(domain => {
                        if (!isDomainInList(domain)) {
                            appendDomainToList(domain);
                        }
                    });

                    // Save the updated list of domains
                    chrome.storage.local.set({ allowedDomains: Array.from(domainSet) });
                });
            } else {
                console.error('Unable to get current tab information');
            }
        });
    }

    // Example function to send domain names to the server
    function sendDomainsToServer(domains) {
        fetch('http://127.0.0.1:5000/api/domains', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ domains: domains }),
        })
            .then(response => response.json())
            .then(data => {
                console.log('Server response:', data);
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }

    // Add event listener for the scan button
    scanButton.addEventListener("click", function () {
        // Check if history is allowed
        if (historyToggle.checked) {
            // Retrieve the list of domains
            const domainItems = allowedDomainsList.querySelectorAll('.domain-item span');
            const domains = Array.from(domainItems).map(item => item.textContent);

            // Perform your scanning logic here
            sendDomainsToServer(domains);
            alert("Scanning all domains!");
        } else {
            alert("No domain to be scanned!");
        }
    });

    function scanAllDomains() {
        // Add your logic here to scan all domains
        alert("Scanning all domains!");
    }

});
