document.addEventListener("DOMContentLoaded", function () {
    // DOM elements
    var unscannedDomainsList = document.getElementById("unscannedDomainsList");
    var allowedDomainsList = document.getElementById("allowedDomainsList");
    var maliciousDomainsList = document.getElementById("maliciousDomainsList");
    var historyToggle = document.getElementById("historyToggle");
    var scanButton = document.getElementById("scanButton");
    var tabs = document.querySelectorAll('.tab');
    var tabContents = document.querySelectorAll('.tab-content');
    var removeButton = document.getElementById("removeButton");

    // Check if necessary elements are present
    if (!unscannedDomainsList || !allowedDomainsList || !maliciousDomainsList || !historyToggle || !scanButton) {
        console.error("Elements not found.");
        return;
    }
      
    chrome.storage.local.get(null, function(result) {
        console.log('Contents of chrome.storage.local:', result);
    });

    // Initialize the extension on page load
    chrome.storage.local.get(['historyEnabled', 'unscannedDomains', 'allowedDomains', 'maliciousDomains'], function (result) {
        historyToggle.checked = result.historyEnabled ?? true;
        populateDomainList(unscannedDomainsList, result.unscannedDomains);
        populateDomainList(allowedDomainsList, result.allowedDomains);
        populateDomainList(maliciousDomainsList, result.maliciousDomains);
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

    // Function to append domain to the list
    function appendDomainToList(list, domain) {
        var newDomainItem = document.createElement("div");
        newDomainItem.className = "domain-item";
        newDomainItem.innerHTML = '<span>' + domain + '</span>' +
            '<button class="remove-btn">X</button>';
        list.appendChild(newDomainItem);
    }

    // Function to check if domain is already in the list
    function isDomainInList(list, domain) {
        var domainItems = list.querySelectorAll('.domain-item span');
        return Array.from(domainItems).some(item => item.textContent === domain);
    }

    // Function to populate domain list, avoiding duplicates
    function populateDomainList(list, domains) {
        console.log(typeof(domains));
        // domains && domains.forEach(domain => {
        //     // Check if the domain already exists in the list
        //     if (!isDomainInList(list, domain)) {
        //         appendDomainToList(list, domain);
        //     }
        // });
    }

    // Event listener for history toggle button
    historyToggle.addEventListener("change", function () {
        if (confirm("Changing this setting may affect your domain list. Are you sure you want to proceed?")) {
            // get history based on toggle state
            if (historyToggle.checked) {
                getUniqueDomainsFromHistory();
            } else {
                console.log("Reading history is disabled.");
            }
            chrome.storage.local.set({ historyEnabled: historyToggle.checked });
        } else {
            historyToggle.checked = !historyToggle.checked;
        }
    });

    // Event listener for the "Remove All Domains" button
    removeButton.addEventListener("click", function () {
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
    });

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

    // Event listener for the scan button
    scanButton.addEventListener("click", function () {
        if (historyToggle.checked) {
            const domainItems = unscannedDomainsList.querySelectorAll('.domain-item span');
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
                        populateDomainList(unscannedDomainsList, domain);
                    });

                    chrome.storage.local.set({ unscannedDomains: Array.from(domainSet) });
                });
            } else {
                console.error('Unable to get current tab information');
            }
        });
    }
});
