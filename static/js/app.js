/* =========================================
   SKILLSWAP — FRONTEND INTERACTIONS
========================================= */

document.addEventListener("DOMContentLoaded", function () {

    /* -----------------------------------------
       SEARCH INPUT
    ----------------------------------------- */

    const searchInput = document.querySelector(
        'input[name="search"]'
    );

    if (searchInput) {

        searchInput.addEventListener("keydown", function (event) {

            if (event.key === "Enter") {

                const form = searchInput.closest("form");

                if (form) {
                    form.submit();
                }

            }

        });

    }


    /* -----------------------------------------
       BUTTON CLICK FEEDBACK
    ----------------------------------------- */

    document.querySelectorAll("button").forEach(function (button) {

        button.addEventListener("click", function () {

            if (
                button.type !== "submit" &&
                !button.classList.contains("mobile-menu-btn")
            ) {

                button.style.transform = "scale(.97)";

                setTimeout(function () {

                    button.style.transform = "";

                }, 120);

            }

        });

    });


    /* -----------------------------------------
       FORM SUBMIT PROTECTION
       Prevent accidental double submission
    ----------------------------------------- */

    document.querySelectorAll("form").forEach(function (form) {

        form.addEventListener("submit", function () {

            const submitButton =
                form.querySelector('button[type="submit"]');

            if (!submitButton) {
                return;
            }

            /*
             * Don't disable search forms.
             */
            if (
                form.querySelector('input[name="search"]')
            ) {
                return;
            }

            /*
             * Small visual feedback.
             */
            submitButton.style.opacity = "0.75";
            submitButton.style.pointerEvents = "none";

            const originalText =
                submitButton.innerHTML;

            submitButton.innerHTML =
                "Processing...";

            /*
             * Safety fallback.
             */
            setTimeout(function () {

                submitButton.style.opacity = "";
                submitButton.style.pointerEvents = "";
                submitButton.innerHTML = originalText;

            }, 5000);

        });

    });


    /* -----------------------------------------
       GIG CARD INTERACTION
    ----------------------------------------- */

    document.querySelectorAll(".gig-card").forEach(function (card) {

        card.addEventListener("mouseenter", function () {

            card.classList.add("is-hovered");

        });

        card.addEventListener("mouseleave", function () {

            card.classList.remove("is-hovered");

        });

    });


    /* -----------------------------------------
       SMOOTH CATEGORY NAVIGATION
    ----------------------------------------- */

    document.querySelectorAll(
        'a[href*="?category="]'
    ).forEach(function (link) {

        link.addEventListener("click", function () {

            /*
             * Let Flask handle the actual navigation.
             * This only gives the browser a small visual
             * feedback before navigation.
             */

            document.body.classList.add(
                "page-loading"
            );

        });

    });


    /* -----------------------------------------
       REMOVE LOADING STATE
    ----------------------------------------- */

    window.addEventListener("pageshow", function () {

        document.body.classList.remove(
            "page-loading"
        );

    });


    /* -----------------------------------------
       AUTO FOCUS SEARCH
       Only on desktop
    ----------------------------------------- */

    if (
        searchInput &&
        window.innerWidth > 850
    ) {

        /*
         * Don't automatically focus if user is
         * already inside another form.
         */
        if (
            document.activeElement === document.body
        ) {
            // Intentionally left without autofocus.
        }

    }

});