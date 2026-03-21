(function () {
    var btn = document.querySelector('.hamburger');
    var nav = document.querySelector('.main-nav');

    if (!btn || !nav) return;

    btn.addEventListener('click', function () {
        var isOpen = nav.classList.toggle('is-open');
        btn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });

    nav.querySelectorAll('a').forEach(function (link) {
        link.addEventListener('click', function () {
            nav.classList.remove('is-open');
            btn.setAttribute('aria-expanded', 'false');
        });
    });

    document.addEventListener('click', function (e) {
        if (!nav.contains(e.target) && !btn.contains(e.target)) {
            nav.classList.remove('is-open');
            btn.setAttribute('aria-expanded', 'false');
        }
    });
})();
