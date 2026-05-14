(function () {
    var storageKey = 'cookie-consent';
    var existingDecision = localStorage.getItem(storageKey);

    if (existingDecision === 'accepted' || existingDecision === 'rejected') {
        return;
    }

    function closeBanner(banner) {
        if (banner && banner.parentNode) {
            banner.parentNode.removeChild(banner);
        }
    }

    function saveDecision(value, banner) {
        localStorage.setItem(storageKey, value);

        if (value === 'accepted' && typeof window.acceptAllCookies === 'function') {
            window.acceptAllCookies();
        }

        if (value === 'rejected' && typeof window.rejectAllCookies === 'function') {
            window.rejectAllCookies();
        }

        closeBanner(banner);
    }

    function createBanner() {
        var banner = document.createElement('div');
        banner.className = 'cookie-banner';
        banner.setAttribute('role', 'dialog');
        banner.setAttribute('aria-live', 'polite');
        banner.setAttribute('aria-labelledby', 'cookie-banner-title');

        banner.innerHTML = [
            '<div class="cookie-banner__inner">',
            '  <p id="cookie-banner-title" class="cookie-banner__text">We use cookies to improve the performance of this site. You can accept or reject cookies.</p>',
            '  <div class="cookie-banner__actions">',
            '    <button type="button" class="cookie-banner__btn" data-consent="accepted">Accept</button>',
            '    <button type="button" class="cookie-banner__btn" data-consent="rejected">Reject</button>',
            '  </div>',
            '</div>'
        ].join('');

        banner.addEventListener('click', function (event) {
            var target = event.target;
            if (!(target instanceof HTMLElement)) return;

            var decision = target.getAttribute('data-consent');
            if (!decision) return;

            saveDecision(decision, banner);
        });

        document.body.appendChild(banner);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createBanner);
    } else {
        createBanner();
    }
})();
