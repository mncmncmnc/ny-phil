(function () {
    var urls = null;
    var loading = null;

    window.nyphilEnsurePrintedProgramUrls = function () {
        if (urls) {
            return Promise.resolve(urls);
        }
        if (loading) {
            return loading;
        }
        var src =
            typeof window.nyphilStaticDataUrl === "function"
                ? window.nyphilStaticDataUrl("printed_program_urls.json")
                : "../data/printed_program_urls.json";
        loading = fetch(src)
            .then(function (r) {
                if (!r.ok) {
                    throw new Error("printed_program_urls missing");
                }
                return r.json();
            })
            .then(function (data) {
                urls = data || {};
                return urls;
            })
            .catch(function () {
                urls = {};
                return urls;
            });
        return loading;
    };

    window.nyphilPrintedProgramHref = function (programId) {
        if (programId == null || programId === "") {
            return null;
        }
        if (!urls) {
            return null;
        }
        return urls[String(programId)] || null;
    };

    /** Configure an <a> for a printed program. Returns false if unavailable. */
    window.nyphilBindProgramLink = function (a, programId, label) {
        a.textContent = label || "program";
        a.target = "_blank";
        a.rel = "noopener noreferrer";
        var href = window.nyphilPrintedProgramHref(programId);
        if (href) {
            a.href = href;
            a.removeAttribute("title");
            a.classList.remove("program-link-unavailable");
            return true;
        }
        a.removeAttribute("href");
        a.classList.add("program-link-unavailable");
        a.title = "Printed program not available";
        return false;
    };
})();
