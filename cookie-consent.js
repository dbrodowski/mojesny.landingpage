(function () {
    var storageKey = 'mojesny_cookie_consent';
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
        closeBanner(banner);
    }

    function createBanner() {
        var banner = document.createElement('div');
        banner.className = 'cookie-banner';
        banner.setAttribute('role', 'dialog');
        banner.setAttribute('aria-live', 'polite');
        banner.setAttribute('aria-label', 'Baner zgody na pliki cookie');

        banner.innerHTML = [
            '<div class="cookie-banner__inner">',
            '  <p class="cookie-banner__text">Używamy plików cookie, aby poprawić działanie strony. Możesz zaakceptować lub odrzucić cookies.</p>',
            '  <div class="cookie-banner__actions">',
            '    <button type="button" class="cookie-banner__btn" data-consent="accepted">Akceptuję</button>',
            '    <button type="button" class="cookie-banner__btn" data-consent="rejected">Odrzucam</button>',
            '  </div>',
            '</div>'
        ].join('');

        banner.addEventListener('click', function (event) {
            var target = event.target;
            if (!(target instanceof HTMLElement)) {
                return;
            }

            var decision = target.getAttribute('data-consent');
            if (!decision) {
                return;
            }

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
