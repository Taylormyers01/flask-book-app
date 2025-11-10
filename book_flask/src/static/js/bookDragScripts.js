const spineColor = new Map([
    ["READ", "#545C52"],
    ["READING", "#C9CBA3"],
    ["WANT_TO_READ", "#ABA9C3"],
    ["NONE", "#723D46"],

])
$(function () {
    const $board = $("#board");
    const boardOffset = $board.offset();
    let displayedBook = null;


    // Make them draggable
    $(".draggable").draggable({
        containment: "#board",
        revert: "invalid",
        zIndex: 1000,
        stack: ".draggable",
        helper: "clone", // ensures we drag the same element, but keep mouse alignment right
        cursorAt: {top: 75, left: 25},


        start: function (event, ui) {
            const $el = $(this);

            // Record original position for reset
            $el.data("origPosition", {
                parent: $el.parent(),
                index: $el.index()
            });


            // Switch to absolute positioning relative to board
            $el.appendTo($board).css({
                position: "absolute",
                width: "50px",
                height: "150px",
                // "z-index": 1000,
                cursor: "grab",
                "text-align": "center",
                "writing-mode": "vertical-rl",
                margin: "unset",
                opacity: 0
            });
            const off = $el.offset();
            // Fix the misalignment by updating draggable's internal offset
            ui.helper.css({
                width: "50px",
                height: "150px",
                "z-index": "1000",
                "text-align": "center",
                "writing-mode": "vertical-rl",
            });
        },

        stop: function (event, ui) {
            const $el = $(this);
            const success = $el.data("dropSuccess");

            if (!success) {
                // Reset styles and put back
                const orig = $el.data("origPosition");
                if (orig && orig.parent.length) {
                    $el.css({
                        position: "",
                        top: "",
                        left: "",
                        width: "",
                        height: "",
                        "z-index": "",
                        cursor: "default",
                        "writing-mode": "horizontal-tb",
                        // "margin-bottom": ".25rem",
                        opacity: 1
                    });

                    $el.removeClass("book-vertical").addClass("book-horizontal");

                    const assigned = $el.data("assigned")
                    console.log("assigned: ", assigned)
                    var newParent = $("#book-stack");
                    if (assigned === true) {
                        console.log("Re-parenting")
                        const book = $el.data("book")
                        saveBookPosition(book.ol_id, null)
                        newParent.append($el)
                    } else if (orig.index >= orig.parent.children().length) {
                        orig.parent.append($el);
                    } else {
                        orig.parent.children().eq(orig.index).before($el);
                    }
                }
            } else {
                const dropEle = $el.data("dropEle");
                $el.appendTo(dropEle)
                $el.css({
                    position: "sticky",
                });
                //     Reset dropSuccess
                $el.data("dropSuccess", false)
            }
        },
    }).data({
        "dropSuccess": false,
        "assigned": false
    }).click(function (event, ui) {
        const el = $(this)
        const book = el.data("book")
        var bookView = $("#bookView")

        displayedBook = book
        bookView.data("book", book)
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
        bookView.show()

    });


    // Make slots droppable
    $(".droppable").droppable({
        accept: ".draggable",
        hoverClass: "highlight",
        drop: function (event, ui) {
            const $drop = $(this);
            const dropOff = $drop.offset(); // doc coords
            const targetTop = dropOff.top - boardOffset.top + ($drop.outerHeight() - ui.draggable.outerHeight()) / 2;
            const targetLeft = dropOff.left - boardOffset.left + ($drop.outerWidth() - ui.draggable.outerWidth()) / 2;

            const dropPosition = $drop.data("position")
            const book = ui.draggable.data("book")
            if (book.shelf_pos === null || book.shelf_pos !== dropPosition) {
                if (saveBookPosition2(book.ol_id, dropPosition) === false) {
                    console.log('failed to save')
                    return
                }
            }
            ui.draggable.data({
                    "dropSuccess": true,
                    "dropEle": $drop,
                    "assigned": true
                }
            ).data("dropEle", $drop).data();

            ui.draggable.animate({top: targetTop, left: targetLeft}, 200, function () {
                ui.draggable.css({
                    cursor: "default",
                    opacity: 1,
                });
            });

        }
    })
    autoPlaceBooks();
    setColors();
});

function autoPlaceBooks() {
    const $board = $("#board");
    const boardOffset = $board.offset();

    $(".draggable").each(function () {
        const $drag = $(this);
        const book = $drag.data("book")
        const assigned = book.shelf_pos != null

        // Example: check flag stored in data attribute
        if (assigned === true) {
            const off = $drag.offset();

            $drag.css({
                top: off.top - boardOffset.top,
                left: off.left - boardOffset.left,
                width: "50px",
                height: "150px",
            })

            const $drop = $("#" + book.shelf_pos + "-drop");
            const dropOff = $drop.offset(); // doc coords
            const targetTop = dropOff.top - boardOffset.top + ($drop.outerHeight() - $drag.outerHeight()) / 2;
            const targetLeft = dropOff.left - boardOffset.left + ($drop.outerWidth() - $drag.outerWidth()) / 2;

            const dropPosition = $drop.data("position")
            console.log(book.ol_id, dropPosition)
            $drag.data({
                    "dropEle": $drop,
                    "assigned": assigned,
                    "dropSuccess": false
                }
            )

            $drag.animate({top: targetTop, left: targetLeft}, 800);

            $drag.appendTo($drop)
            $drag.css({
                position: "sticky",
                opacity: 1,
                margin: "unset",
            });
        }
    });
}

function setColors(){
    $(".draggable").each(function () {
        const $drag = $(this);
        const book = $drag.data("book");

        $drag.css({
            "background-color": spineColor.get(book.status)
        })
    });
}


function saveBookPosition(ol_id, position) {

    const output = fetch("/update-bookshelf-order", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            ol_id: ol_id,
            position: position
        }),
    })
        .then(response => {
            if (!response.ok) {
                throw new Error("Error while saving book position");
            }
            return response.json();
        })
        .then(data => {
            console.log("Position saved:", data);
            return true;
        })
        .catch(error => {
            console.error("Error saving position:", error);
            return false;
        });
    console.log("saved: ", output)
    return output;
}

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

