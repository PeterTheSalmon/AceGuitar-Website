document.addEventListener('DOMContentLoaded', function () {
    console.log('Platform links script loaded.');

    var userAgent = navigator.userAgent || navigator.vendor || window.opera;
    console.log('User Agent:', userAgent);

    var downloadButton = document.getElementById('download-button'); // Homepage main button
    var navbarDownloadButton = document.getElementById('navbar-download-button'); // Navbar button
    var downloadPageAppStoreButton = document.getElementById('download-page-appstore-button'); // Download page App Store button

    if (!navbarDownloadButton) {
        console.error('Navbar download button (navbar-download-button) not found!');
    } else {
        console.log('Navbar download button found:', navbarDownloadButton);
    }
    if (!downloadButton) {
        console.warn('Main download button (download-button) not found on this page.');
    } else {
        console.log('Main download button found:', downloadButton);
    }
    if (!downloadPageAppStoreButton) {
        console.warn('Download page App Store button (download-page-appstore-button) not found on this page.');
    } else {
        console.log('Download page App Store button found:', downloadPageAppStoreButton);
    }

    var isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    var iOS = (/iPad|iPhone|iPod/.test(userAgent) ||
        (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1))
        && !window.MSStream;
    var macOS = /Macintosh/.test(userAgent) && !iOS && !isTouchDevice;

    console.log('Is iOS?', iOS);
    console.log('Is macOS?', macOS);

    var appStoreLink = 'https://apps.apple.com/us/app/aceguitar-learn-play/id6739484277';
    var downloadPageLink = '/download';

    if (iOS || macOS) {
        console.log('Detected Apple platform. Setting links to App Store.');
        if (navbarDownloadButton) {
            navbarDownloadButton.href = appStoreLink;
            navbarDownloadButton.target = '_blank';
            navbarDownloadButton.rel = 'noopener noreferrer';
            console.log('Navbar button href set to:', appStoreLink, 'and target to _blank');
        }
        if (downloadButton) { // Homepage main button
            downloadButton.href = appStoreLink;
            downloadButton.target = '_blank';
            downloadButton.rel = 'noopener noreferrer';
            console.log('Main download button (homepage) href set to:', appStoreLink, 'and target to _blank');
        }
        if (downloadPageAppStoreButton) { // Download page App Store button
            // downloadPageAppStoreButton.href = appStoreLink; // Link is already correct in HTML
            downloadPageAppStoreButton.target = '_blank'; // Ensure target is _blank
            downloadPageAppStoreButton.rel = 'noopener noreferrer'; // Ensure rel is set
            console.log('Download page App Store button target set to _blank');
        }
    } else {
        console.log('Detected non-Apple platform. Setting links to /download page.');
        if (navbarDownloadButton) {
            navbarDownloadButton.href = downloadPageLink;
            navbarDownloadButton.target = ''; // Reset target
            navbarDownloadButton.rel = '';
            console.log('Navbar button href set to:', downloadPageLink);
        }
        if (downloadButton) { // Homepage main button
            downloadButton.href = downloadPageLink;
            downloadButton.target = ''; // Reset target
            downloadButton.rel = '';
            console.log('Main download button (homepage) href set to:', downloadPageLink);
        }
        if (downloadPageAppStoreButton) { // Download page App Store button
            // For non-Apple, ensure it still goes to App Store but opens in same tab if script somehow ran on it
            // However, the HTML already has target=_blank, so we only need to ensure it's not overridden by this script for non-Apple
            // The link itself is static in the HTML for this button.
            // We can explicitly set target to _blank here as well to be safe, as it should always open App Store in new tab.
            downloadPageAppStoreButton.target = '_blank';
            downloadPageAppStoreButton.rel = 'noopener noreferrer';
            console.log('Download page App Store button target maintained as _blank for non-Apple (link is static).');
        }
    }
    console.log('Platform links script finished.');
});
