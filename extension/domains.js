document.addEventListener("DOMContentLoaded", function () {
    var allowedDomainsList = document.getElementById("allowedDomainsList");
    var historyToggle = document.getElementById("historyToggle"); // Access the toggle button

    if (!allowedDomainsList || !historyToggle) {
        console.error("Elements not found.");
        return;
    }

    // Load saved settings and domains
    chrome.storage.local.get(['historyEnabled', 'allowedDomains', 'manualDomains'], function (result) {
        historyToggle.checked = result.historyEnabled ?? true; // Default to true if undefined

        // Append domains from history
        (result.allowedDomains ?? []).forEach(domain => appendDomainToList(domain));

        // Append manually added domains
        (result.manualDomains ?? []).forEach(domain => appendDomainToList(domain));

        // Adjust based on the loaded toggle state
        conditionalGetHistory();
    });

    function conditionalGetHistory() {
        if (historyToggle.checked) {
            getUniqueDomainsFromHistory();
        } else {
            console.log("Reading history is disabled.");
            clearDomainsList(); // Call to clear the domains list if toggled off
        }
    }

    historyToggle.addEventListener("change", function () {
        conditionalGetHistory();
        // Save the toggle state to storage
        chrome.storage.local.set({ historyEnabled: historyToggle.checked });
    });

    function clearDomainsList() {
        while (allowedDomainsList.firstChild) {
            allowedDomainsList.removeChild(allowedDomainsList.firstChild);
        }
        console.log("Domains list cleared.");
    }

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

    function removeDomain(button, domain) {
        button.closest('.domain-item').remove();
        console.log("Domain removed successfully");

        // Determine if the removed domain was manually added or from history
        chrome.storage.local.get(['manualDomains'], function (result) {
            const manualDomains = result.manualDomains ?? [];

            if (manualDomains.includes(domain)) {
                // Remove the domain from manually added domains
                chrome.storage.local.set({
                    manualDomains: manualDomains.filter(d => d !== domain)
                });
            } else {
                // Remove the domain from history (allowedDomains)
                chrome.storage.local.get(['allowedDomains'], function (result) {
                    const updatedDomains = (result.allowedDomains ?? []).filter(d => d !== domain);
                    chrome.storage.local.set({ allowedDomains: updatedDomains });
                });
            }
        });
    }

    function isDomainInList(domain) {
        var domainItems = allowedDomainsList.querySelectorAll('.domain-item span');
        return Array.from(domainItems).some(item => item.textContent === domain);
    }

    function appendDomainToList(domain) {
        if (!isDomainInList(domain)) {
            var newDomainItem = document.createElement("div");
            newDomainItem.className = "domain-item";
            newDomainItem.innerHTML = '<span>' + domain + '</span><button class="remove-btn">X</button>';
            allowedDomainsList.appendChild(newDomainItem);
        }
    }

    function getUniqueDomainsFromHistory() {
        const microsecondsPerWeek = 1000 * 60 * 60 * 24 * 7;
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

                    // Save the updated list of domains to allowedDomains
                    chrome.storage.local.set({ allowedDomains: Array.from(domainSet) });
                });
            } else {
                console.error('Unable to get current tab information');
            }
        });
    }
});
