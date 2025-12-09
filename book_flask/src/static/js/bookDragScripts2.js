// book-drag-rewrite.js
(function ($) {
    "use strict";

    const spineColor = new Map([
        ["READ", "#545C52"],
        ["READING", "#C9CBA3"],
        ["WANT_TO_READ", "#ABA9C3"],
        ["NONE", "#723D46"]
    ]);

    // Utility: rect helpers using getBoundingClientRect for cross-browser consistency
    function rect(el) {
        const r = el.getBoundingClientRect();
        return { left: r.left, top: r.top, width: r.width, height: r.height };
    }

    // Create a visual clone helper (absolute positioned in body) and return it (jQuery)
    function makeHelper($orig) {
        const o = rect($orig[0]);
        const $h = $orig.clone(true);
        $h.addClass("drag-helper-temp");
        // reset any layout-affecting classes
        $h.css({
            position: "absolute",
            left: o.left + window.scrollX,
            top: o.top + window.scrollY,
            width: o.width,
            height: o.height,
            margin: 0,
            zIndex: 9999,
            pointerEvents: "none",
            opacity: 1,
            "writing-mode": $orig.css("writing-mode") || ""
        });
        $("body").append($h);
        return $h;
    }

    // Animate helper from current position to target rect (page coords). returns Promise
    function animateHelperTo($helper, targetPageLeft, targetPageTop, ms = 200) {
        return new Promise(resolve => {
            $helper.animate(
                {
                    left: Math.round(targetPageLeft),
                    top: Math.round(targetPageTop)
                },
                {
                    duration: ms,
                    easing: "swing",
                    complete: () => resolve()
                }
            );
        });
    }

    // Move original element into the drop slot and normalize styles so it flows
    function finalizePlacement($orig, $drop) {
        $orig.appendTo($drop);
        // Ensure correct size/appearance once it's in the drop
        $orig.css({
            position: "relative",
            top: "",
            left: "12px",
            width: "50px",
            height: "150px",
            margin: "unset",
            opacity: 1,
            "writing-mode": "vertical-rl",
            cursor: "default",
            visibility: ""
        });
        $orig.removeClass("book-horizontal").addClass("book-vertical");
        $orig.data({ dropEle: $drop, assigned: true, dropSuccess: false });
    }

    // Revert helper and remove
    function removeHelper($h) {
        $h.remove();
    }

    // Expose saveBookPosition2 as an async function that throws on failure.
    // If you already have saveBookPosition2 defined globally, this wrapper will call it.
    async function savePosOrThrow(ol_id, position) {
        // If the user provided saveBookPosition2 as in previous code, call it and try to detect failure.
        // That function may not return a boolean. We'll call it and treat it as optimistic (no throw) unless it throws.
        if (typeof window.saveBookPosition2 === "function") {
            try {
                // call and await in case it returns a promise
                const maybe = window.saveBookPosition2(ol_id, position);
                if (maybe && typeof maybe.then === "function") {
                    // await the promise (if it resolves to false/undefined, we still continue)
                    await maybe;
                }
                return;
            } catch (err) {
                throw err;
            }
        } else {
            // No backend save function defined: just continue (optimistic)
            return;
        }
    }

    $(function () {
        const $board = document.getElementById("board");
        if (!$board) {
            console.warn("board element (#board) not found — aborting drag init");
            return;
        }

        // apply colors
        function setColors() {
            $(".draggable").each(function () {
                const book = $(this).data("book");
                if (book && book.status) $(this).css("background-color", spineColor.get(book.status));
            });
        }

        // click behavior preserved
        $(".draggable").off("click").on("click", function () {
            const el = $(this);
            const book = el.data("book");
            const bookView = $("#bookView");
            bookView.data("book", book);
            $("#bookTitle").text(book.title).css("font-weight", "bold");
            $("#bookAuthor").text("by " + book.author);
            $("#bookDesc").text(book.description);
            $("#bookOwned").text(book.owned ? "Yes" : "No");
            $("#bookStatus").text(book.status || "Not set");
            if (book.thumbnail) {
                $("#bookImg").attr("src", book.thumbnail).show();
            } else {
                $("#bookImg").hide();
            }
            bookView.show();
        });

        // Initialize jQuery UI draggable — but we will use our own helper lifecycle in the events
        $(".draggable").draggable({
            helper: function () {
                // We return an empty element here because we'll manage our own helper for animation.
                // But we still want jQuery UI's internal helper to exist so revert/dragging works.
                // Returning a clone so UI shows immediate visual while we create our own exact clone for animation later.
                const $c = $(this).clone();
                $c.css({ width: $(this).outerWidth(), height: $(this).outerHeight() });
                return $c;
            },
            appendTo: "body",
            // containment: "#board",
            zIndex: 2000,
            revert: "invalid",
            start: function (event, ui) {
                // store original rect and parent info
                const $orig = $(this);
                const r = rect(this);
                $orig.data("origInfo", {
                    parent: $orig.parent(),
                    index: $orig.index(),
                    pageLeft: r.left + window.scrollX,
                    pageTop: r.top + window.scrollY,
                    width: r.width,
                    height: r.height
                });

                // Ensure helper visually matches
                ui.helper.css({
                    width: r.width,
                    height: r.height,
                    "writing-mode": $orig.css("writing-mode") || "",
                    textAlign: $orig.css("text-align") || "center"
                });
            },
            stop: function (event, ui) {
                // nothing: actual placement handled in droppable drop
            }
        });

        // DROPPABLE logic using page coords (getBoundingClientRect)
        $(".droppable").droppable({
            accept: ".draggable",
            hoverClass: "highlight",
            drop: function (event, ui) {
                const $drop = $(this);
                const $orig = ui.draggable; // original element (jQuery)
                const book = $orig.data("book");
                const dropPosIndex = $drop.data("position");

                // compute original page rect and drop target page rect
                const origRect = rect($orig[0]);
                const dropRect = rect($drop[0]);
                const boardRect = rect($board);

                // compute target page coords (centered in drop)
                const targetPageLeft = dropRect.left + (dropRect.width - origRect.width) / 2 + window.scrollX;
                const targetPageTop = dropRect.top + (dropRect.height - origRect.height) / 2 + window.scrollY;

                // create animator helper at original's page location
                const $anim = makeHelper($orig);

                // hide original visually while animating (but keep it in DOM to preserve layout)
                $orig.css({ visibility: "hidden" });

                // attempt to save position (await). If save fails we revert.
                (async () => {
                    try {
                        await savePosOrThrow(book.ol_id, dropPosIndex);
                    } catch (err) {
                        // revert: remove helper, unhide original
                        removeHelper($anim);
                        $orig.css({ visibility: "visible" });
                        console.error("Failed to save position:", err);
                        return;
                    }

                    // animate helper to target page coords
                    await animateHelperTo($anim, targetPageLeft, targetPageTop, 180);

                    // after animation: remove helper and append original into drop
                    removeHelper($anim);
                    finalizePlacement($orig, $drop);
                })();
            }
        });

        $("#book-stack").droppable({
            accept: ".draggable",
            hoverClass: "highlight",
            drop: function (event, ui) {
                const $drop = $(this);
                const $orig = ui.draggable; // original element (jQuery)
                const book = $orig.data("book");

                // compute original page rect and drop target page rect
                const origRect = rect($orig[0]);
                const dropRect = rect($drop[0]);
                const boardRect = rect($board);

                // compute target page coords (centered in drop)
                const targetPageLeft = dropRect.left + (dropRect.width - origRect.width) / 2 + window.scrollX;
                const targetPageTop = dropRect.top + (dropRect.height - origRect.height) / 2 + window.scrollY;

                // create animator helper at original's page location
                const $anim = makeHelper($orig);
                (async () => {
                    try {
                        await savePosOrThrow(book.ol_id, null);
                    } catch (err) {
                        // revert: remove helper, unhide original
                        removeHelper($anim);
                        $orig.css({ visibility: "visible" });
                        console.error("Failed to save position:", err);
                        return;
                    }

                    // animate helper to target page coords
                    await animateHelperTo($anim, targetPageLeft, targetPageTop, 180);

                    // after animation: remove helper and append original into drop
                    removeHelper($anim);
                    $orig.appendTo($drop);
                    // Ensure correct size/appearance once it's in the drop
                    $orig.css({
                        position: "relative",
                        top: "",
                        left: "",
                        width: "150px",
                        height: "50px",
                        margin: "unset",
                        opacity: 1,
                        "writing-mode": "horizontal-tb",
                        cursor: "default",
                        visibility: ""
                    });
                    $orig.data({ dropEle: $drop, assigned: true, dropSuccess: false });
                })();
            }
        });

        // autoPlaceBooks: use same clone-animate-append approach
        async function autoPlaceBooks() {
            const $drags = $(".draggable");
            if (!$drags.length) return;

            $drags.each(function () {
                const $drag = $(this);
                const book = $drag.data("book");
                if (!book || book.shelf_pos === null || book.shelf_pos === undefined) return;

                const $drop = $("#" + book.shelf_pos + "-drop");
                if (!$drop.length) return;

                // compute rects
                const origRect = rect($drag[0]);
                const dropRect = rect($drop[0]);

                const targetPageLeft = dropRect.left + (dropRect.width - origRect.width) / 2 + window.scrollX;
                const targetPageTop = dropRect.top + (dropRect.height - origRect.height) / 2 + window.scrollY;

                // create helper clone at original location
                const $anim = makeHelper($drag);

                // hide original while animating
                $drag.css({ visibility: "hidden" });

                // animate and append when done
                animateHelperTo($anim, targetPageLeft, targetPageTop, 350).then(() => {
                    removeHelper($anim);
                    finalizePlacement($drag, $drop);
                });
            });
        }

        // run initial placement and coloring
        autoPlaceBooks();
        setColors();

        // expose setColors and autoPlaceBooks should you want to call them externally
        window.bookDragSetColors = setColors;
        window.bookDragAutoPlace = autoPlaceBooks;
    });
})(jQuery);

// Update book position in DB
async function saveBookPosition2(ol_id, position) {
    const url = "/update-bookshelf-order";
    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                ol_id: ol_id,
                position: position
            })
        });
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }
        const result = await response.json();
        console.log(result);
    } catch (error) {
        console.error(error.message);
    }
}
