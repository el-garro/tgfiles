// My own htmx extension to provide extra indicators

document.head.insertAdjacentHTML("beforeend",
    "<style>\
.htmx-error-indicator {display: none;}\
.htmx-error .htmx-error-indicator {display: inline;}\
.htmx-done-indicator {display: none;}\
.htmx-done .htmx-done-indicator {display: block;}\
</style>")

htmx.defineExtension('better-indicators', {
    onEvent: function (name, evt) {
        if (name === "htmx:trigger") {
            evt.detail.elt.classList.remove("htmx-error");
            evt.detail.elt.classList.remove("htmx-done");
        }

        if (name === "htmx:responseError" || name === "htmx:sendError") {
            evt.detail.elt.classList.add("htmx-error");
        }


        if (name === "htmx:afterRequest" && !evt.detail.elt.classList.contains("htmx-error")) {
            evt.detail.elt.classList.add("htmx-done");
        }

        return true;
    }
})
