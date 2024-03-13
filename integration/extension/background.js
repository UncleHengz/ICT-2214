// // background.js

// let scanning = false;
// let loadingInterval;
// let timeoutIds = [];

// function updateProgress(percentage) {
//     // Your implementation for updating progress
//     console.log('Updating progress:', percentage);
// }

// function performScan() {
//     scanning = true;

//     let i = 0;
//     loadingInterval = setInterval(function () {
//         updateProgress(i);
//         i += 10;
//         if (i > 100) {
//             clearInterval(loadingInterval);
//             completeScan();
//         }
//     }, 1000);

//     timeoutIds.push(loadingInterval);
// }

// function resetScan() {
//     timeoutIds.forEach(clearTimeout);
//     scanning = false;
//     // Your implementation for resetting scan
//     console.log('Scan reset.');
// }

// function completeScan() {
//     timeoutIds.forEach(clearTimeout);
//     // Your implementation for completing the scan
//     console.log('Scan complete.');
// }

// chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
//     if (request.action === 'startScan') {
//         performScan();
//     } else if (request.action === 'stopScan') {
//         resetScan();
//     }
// });
