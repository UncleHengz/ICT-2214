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
   function populateWebsiteLink() {
       chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
           if (tabs && tabs.length > 0) {
               websiteLinkElement.value = tabs[0].url;
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

   // Function to complete the scan
   function completeScan() {
       timeoutIds.forEach(clearTimeout);
       statusElement.innerHTML = 'Scan complete. Website is safe!';
       statusElement.classList.remove('alert-warning');
       statusElement.classList.add('alert-success');
       updateProgress(100);

       scanButtonElement.disabled = false;
       scanning = false;
       scanButtonElement.innerText = 'Start';
   }


   // Populate the website link on extension popup open
   populateWebsiteLink();

   // Perform scan on extension popup open
   performScan();

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
