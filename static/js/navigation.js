/**
 * Navigation helper script
 * This script fixes navigation issues with class enrollment pages and prevents
 * the main script.js from trying to use page URLs as CSS selectors
 */
document.addEventListener('DOMContentLoaded', function() {
    // Get the current path
    const currentPath = window.location.pathname;
    
    // Highlight active navigation item based on current path
    document.querySelectorAll('.navbar a').forEach(link => {
        const linkHref = link.getAttribute('href');
        
        // If this is a page link (not an anchor)
        if (linkHref && linkHref.startsWith('/')) {
            // For exact matches
            if (linkHref === currentPath) {
                link.classList.add('active');
            }
            // For partial matches (e.g. /class/1 should highlight /classes)
            else if ((currentPath.startsWith('/class/') && linkHref === '/classes') ||
                     (currentPath.startsWith(linkHref) && linkHref !== '/')) {
                link.classList.add('active');
            }
              // Fix the error with querySelector - prevent default only for non-page links
            link.addEventListener('click', function(e) {
                // Let the browser handle the navigation normally
                // The script.js already has logic to return early for page nav links
            });
        }
    });
});
