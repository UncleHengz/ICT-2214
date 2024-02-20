document.addEventListener("DOMContentLoaded", function () {
    var allowedDomainsList = document.getElementById("allowedDomainsList");
    var addButton = document.querySelector(".add-btn");

    if (!allowedDomainsList || !addButton) {
        console.error("Elements not found.");
        return;
    }

    // Event delegation for the Remove button clicks
    allowedDomainsList.addEventListener("click", function (event) {
        var removeButton = event.target.closest('.remove-btn');
        if (removeButton) {
            var domainItem = removeButton.closest('.domain-item');
            var removedDomainText = domainItem.querySelector('span').textContent;
            if (confirm("Are you sure you want to remove domain '" + removedDomainText + "'?")) {
                removeDomain(removeButton);
            }
        }
    });

    addButton.addEventListener("click", function () {
        // Get the current URL from the active tab
        chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
            if (tabs && tabs.length > 0) {
                var currentDomain = extractDomain(tabs[0].url);

                // Check if the current domain is already in the list
                if (isDomainInList(currentDomain)) {
                    alert("Domain already in the list.");
                    return;
                }

                // Create a new domain item
                var newDomainItem = document.createElement("div");
                newDomainItem.className = "domain-item";
                newDomainItem.innerHTML = '<span>' + currentDomain + '</span>' +
                                          '<button class="remove-btn">X</button>';

                // Append the new domain item to the list
                allowedDomainsList.appendChild(newDomainItem);
            } else {
                console.error('Unable to get tab URL');
            }
        });
    });

    function removeDomain(button) {
        var domainItem = button.closest('.domain-item');
        domainItem.parentNode.removeChild(domainItem);
        console.log("Domain removed successfully");
    }

    function isDomainInList(domain) {
        var domainItems = allowedDomainsList.querySelectorAll('.domain-item span');
        for (var i = 0; i < domainItems.length; i++) {
            if (domainItems[i].textContent === domain) {
                return true;
            }
        }
        return false;
    }

    // Function to extract domain from a URL
    function extractDomain(url) {
        var domain;
        try {
            domain = new URL(url).hostname;
        } catch (error) {
            console.error('Error extracting domain:', error);
        }
        return domain || url; // Return the full URL if extraction fails
    }
});
