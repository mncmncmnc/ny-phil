(function () {
    var ALLOWED = ["all", "subscription_season"];
    var params = new URLSearchParams(location.search);
    var p = params.get("preset") || "all";
    if (ALLOWED.indexOf(p) === -1) {
        p = "all";
    }
    window.NYPHIL_PRESET = p;

    window.nyphilPresetLabel = function (key) {
        if (key === "subscription_season") {
            return "Subscription season";
        }
        return "All event types";
    };

    window.nyphilDataUrl = function (filename) {
        var root = window.NYPHIL_DATA_ROOT || "../";
        return root + "data/presets/" + window.NYPHIL_PRESET + "/" + filename;
    };

    window.nyphilDateIndicesUrl = function (mm, dd) {
        var root = window.NYPHIL_DATA_ROOT || "../";
        var m = String(mm).padStart(2, "0");
        var d = String(dd).padStart(2, "0");
        return (
            root +
            "data/presets/" +
            window.NYPHIL_PRESET +
            "/date-indices/" +
            m +
            "-" +
            d +
            ".json"
        );
    };

    /** Shared data file outside presets (e.g. location_coordinates.json). */
    window.nyphilStaticDataUrl = function (filename) {
        var root = window.NYPHIL_DATA_ROOT || "../";
        return root + "data/" + filename;
    };

    window.nyphilSwitchPreset = function (preset) {
        var u = new URL(location.href);
        u.searchParams.set("preset", preset);
        location.href = u.pathname + u.search;
    };
})();
