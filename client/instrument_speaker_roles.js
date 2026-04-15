/**
 * Optional chart groupings for soloist-instrument views: spoken-word roles and
 * dance/movement roles (hidden by default; merged or per-key via checkboxes).
 */
(function (global) {
    var MERGED_SPEAKER_LABEL = "Speakers, Actors, and Readers";
    var MERGED_DANCER_LABEL = "Dancers and Movement Artists";

    var SPEAKER_ROLE_KEYS = [
        "actor",
        "actress",
        "author",
        "commentator",
        "dramaturg",
        "female speaker",
        "guest speaker",
        "host",
        "male speaker",
        "narrator",
        "poet",
        "poet / speaker",
        "poetry reader",
        "reader",
        "reciter",
        "speaker",
        "speaker, female",
        "speaker, male",
        "storywriter",
        "writer/narrator",
    ];

    var DANCER_ROLE_KEYS = [
        "actor and dancer",
        "bailaora [flamenco dancer]",
        "choreographer",
        "choreographer/dancer",
        "dance company",
        "dance company / dancer",
        "dancer",
        "drummers and dancers",
        "film dance visualist",
        "flamenco dancer",
        "mime",
        "tap dancer",
    ];

    var SPEAKER_SET = {};
    SPEAKER_ROLE_KEYS.forEach(function (k) {
        SPEAKER_SET[k] = true;
    });
    var DANCER_SET = {};
    DANCER_ROLE_KEYS.forEach(function (k) {
        DANCER_SET[k] = true;
    });

    function isSpeakerRoleKey(key) {
        return !!SPEAKER_SET[key];
    }

    function isDancerRoleKey(key) {
        return !!DANCER_SET[key];
    }

    function nyphilSpeakerRolesMergedLabel() {
        return MERGED_SPEAKER_LABEL;
    }

    function nyphilDancerRolesMergedLabel() {
        return MERGED_DANCER_LABEL;
    }

    function nyphilIsSpeakerRoleInstrument(key) {
        return isSpeakerRoleKey(key);
    }

    function nyphilIsDancerRoleInstrument(key) {
        return isDancerRoleKey(key);
    }

    function sumRoleYears(raw, keys, startYear, endYear) {
        var merged = {};
        for (var y = startYear; y <= endYear; y++) {
            var ys = String(y);
            var sum = 0;
            keys.forEach(function (k) {
                if (raw[k] && raw[k][ys] != null) sum += raw[k][ys];
            });
            merged[ys] = sum;
        }
        return merged;
    }

    /**
     * @param {Record<string, Record<string, number>>} raw
     * @param {number} startYear
     * @param {number} endYear
     * @param {{ includeSpeakers: boolean, speakerBreakdown: boolean, includeDancers: boolean, dancerBreakdown: boolean }} opt
     */
    function nyphilBuildInstrumentChartView(raw, startYear, endYear, opt) {
        var out = {};
        Object.keys(raw).forEach(function (k) {
            if (k === MERGED_SPEAKER_LABEL || k === MERGED_DANCER_LABEL) return;

            var sp = isSpeakerRoleKey(k);
            var dn = isDancerRoleKey(k);

            if (sp && !opt.includeSpeakers) return;
            if (dn && !opt.includeDancers) return;

            if (sp && opt.includeSpeakers && !opt.speakerBreakdown) return;
            if (dn && opt.includeDancers && !opt.dancerBreakdown) return;

            out[k] = raw[k];
        });

        if (opt.includeSpeakers && !opt.speakerBreakdown) {
            out[MERGED_SPEAKER_LABEL] = sumRoleYears(
                raw,
                SPEAKER_ROLE_KEYS,
                startYear,
                endYear
            );
        }

        if (opt.includeDancers && !opt.dancerBreakdown) {
            out[MERGED_DANCER_LABEL] = sumRoleYears(
                raw,
                DANCER_ROLE_KEYS,
                startYear,
                endYear
            );
        }

        return out;
    }

    /** @deprecated use nyphilBuildInstrumentChartView with an options object */
    function nyphilBuildSpeakerAwareInstrumentMap(
        raw,
        startYear,
        endYear,
        includeSpeakers,
        speakerBreakdown,
        includeDancers,
        dancerBreakdown
    ) {
        var incD =
            arguments.length >= 7 ? !!includeDancers : false;
        var brD = arguments.length >= 8 ? !!dancerBreakdown : false;
        return nyphilBuildInstrumentChartView(raw, startYear, endYear, {
            includeSpeakers: !!includeSpeakers,
            speakerBreakdown: !!speakerBreakdown,
            includeDancers: incD,
            dancerBreakdown: brD,
        });
    }

    function blockKeys(viewKeys, mergedLabel, isRoleKey) {
        var hasMerged = viewKeys.indexOf(mergedLabel) !== -1;
        if (hasMerged) return [mergedLabel];
        var ids = viewKeys
            .filter(function (k) {
                return isRoleKey(k);
            })
            .sort(function (a, b) {
                return b.localeCompare(a);
            });
        return ids;
    }

    /**
     * Band / line order: speaker block (bottom), then dancer block, then main instruments.
     */
    function nyphilInstrumentExceptionYDomain(viewKeys) {
        var keys = viewKeys.slice();
        var main = keys
            .filter(function (k) {
                return (
                    k !== MERGED_SPEAKER_LABEL &&
                    k !== MERGED_DANCER_LABEL &&
                    !isSpeakerRoleKey(k) &&
                    !isDancerRoleKey(k)
                );
            })
            .sort(function (a, b) {
                return b.localeCompare(a);
            });

        var sPart = blockKeys(
            keys,
            MERGED_SPEAKER_LABEL,
            isSpeakerRoleKey
        );
        var dPart = blockKeys(
            keys,
            MERGED_DANCER_LABEL,
            isDancerRoleKey
        );

        return sPart.concat(dPart).concat(main);
    }

    /** @deprecated use nyphilInstrumentExceptionYDomain */
    function nyphilSpeakerInstrumentYDomain(viewKeys) {
        return nyphilInstrumentExceptionYDomain(viewKeys);
    }

    global.nyphilSpeakerRolesMergedLabel = nyphilSpeakerRolesMergedLabel;
    global.nyphilDancerRolesMergedLabel = nyphilDancerRolesMergedLabel;
    global.nyphilIsSpeakerRoleInstrument = nyphilIsSpeakerRoleInstrument;
    global.nyphilIsDancerRoleInstrument = nyphilIsDancerRoleInstrument;
    global.nyphilBuildInstrumentChartView = nyphilBuildInstrumentChartView;
    global.nyphilBuildSpeakerAwareInstrumentMap =
        nyphilBuildSpeakerAwareInstrumentMap;
    global.nyphilInstrumentExceptionYDomain = nyphilInstrumentExceptionYDomain;
    global.nyphilSpeakerInstrumentYDomain = nyphilSpeakerInstrumentYDomain;
})(typeof window !== "undefined" ? window : this);
