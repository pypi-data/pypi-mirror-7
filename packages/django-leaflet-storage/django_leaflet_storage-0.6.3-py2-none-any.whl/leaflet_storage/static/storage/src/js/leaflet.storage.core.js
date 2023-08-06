/* Poor man pub/sub handler, enough for now */

L.StorageSingleton = L.Class.extend({
    includes: L.Mixin.Events,
    version: '0.6.0'
});
L.Storage = new L.StorageSingleton();
L.S = L.Storage;
L.Storage.Map = L.Map.extend({});


/*
* Utils
*/
L.Util.queryString = function (name, fallback) {
    var decode = function (s) { return decodeURIComponent(s.replace(/\+/g, " ")); };
    var qs = window.location.search.slice(1).split('&'), qa = {};
    for(var i in qs) {
        var key = qs[i].split('=');
        if (!key) continue;
        qa[decode(key[0])] = key[1] ? decode(key[1]) : 1;
    }
    return qa[name] || fallback;
};

L.Util.booleanFromQueryString = function (name) {
    var value = L.Util.queryString(name);
    return value === "1" || value === "true";
};

L.Util.setFromQueryString = function (options, name) {
    var value = L.Util.queryString(name);
    if (typeof value !== "undefined") {
        options[name] = value;
    }
};

L.Util.setBooleanFromQueryString = function (options, name) {
    var value = L.Util.queryString(name);
    if (typeof value !== "undefined") {
        options[name] = value == "1" || value == "true";
    }
};
L.Util.escapeHTML = function (s) {
    s = s? s.toString() : "";
    return s.replace(/</gm, '&lt;');
};
L.Util.toHTML = function (r) {
    var ii;

    // detect newline format
    var newline = r.indexOf('\r\n') != -1 ? '\r\n' : r.indexOf('\n') != -1 ? '\n' : '';

    // Escape tags
    r = r.replace(/</gm, '&lt;');


    // headings and hr
    r = r.replace(/^### (.*)=*/gm, '<h5>$1</h5>');
    r = r.replace(/^## (.*)=*/gm, '<h4>$1</h4>');
    r = r.replace(/^# (.*)=*/gm, '<h3>$1</h3>');
    r = r.replace(/^[-*][-*][-*]+/gm, '<hr>');

    // bold, italics
    r = r.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    r = r.replace(/\*(.*?)\*/g, '<em>$1</em>');

    // unordered lists
    r = r.replace(/^\*\* (.*)/gm, '<ul><ul><li>$1</li></ul></ul>');
    r = r.replace(/^\* (.*)/gm, '<ul><li>$1</li></ul>');
    for (ii = 0; ii < 3; ii++) r = r.replace(new RegExp('</ul>' + newline + '<ul>', 'g'), newline);

    // links
    r = r.replace(/(\[\[http)/g, '[[h_t_t_p');  // Escape for avoiding clash between [[http://xxx]] and http://xxx
    r = r.replace(/({{http)/g, '{{h_t_t_p');
    r = r.replace(/(https?[^ \)\n]*)/g, '<a target="_blank" href="$1">$1</a>');
    r = r.replace(/\[\[(h_t_t_ps?:[^\]|]*?)\]\]/g, '<a target="_blank" href="$1">$1</a>');
    r = r.replace(/\[\[(h_t_t_ps?:[^|]*?)\|(.*?)\]\]/g, '<a target="_blank" href="$1">$2</a>');
    r = r.replace(/\[\[([^\]|]*?)\]\]/g, '<a href="$1">$1</a>');
    r = r.replace(/\[\[([^|]*?)\|(.*?)\]\]/g, '<a href="$1">$2</a>');

    // iframe
    r = r.replace(/{{{(h_t_t_ps?[^ |]*)}}}/g, '<iframe frameBorder="0" src="$1" width="100%" height="300px"></iframe>');
    r = r.replace(/{{{(h_t_t_ps?[^ |]*)\|(\d*?)}}}/g, '<iframe frameBorder="0" src="$1" width="100%" height="$2px"></iframe>');

    // images
    r = r.replace(/{{([^\]|]*?)}}/g, '<img src="$1">');
    r = r.replace(/{{([^|]*?)\|(\d*?)}}/g, '<img src="$1" width="$2">');

    //Unescape http
    r = r.replace(/(h_t_t_p)/g, 'http');

    // Preserver line breaks
    if (newline) r = r.replace(new RegExp(newline, 'g'), '<br>' + newline);

    return r;
};
L.Util.isObject = function (what) {
    return typeof what === "object" && what !== null;
};
L.Util.latLngsForGeoJSON = function (latlngs) {
    coords = [];
    for(var i = 0, len = latlngs.length; i < len; i++) {
        coords.push([
            latlngs[i].lng,
            latlngs[i].lat
        ]);
    }
    return coords;
};
L.Util.CopyJSON = function (geojson) {
    return JSON.parse(JSON.stringify(geojson));
}
L.Util.detectFileType = function (f) {
    var filename = f.name ? escape(f.name.toLowerCase()) : '';
    function ext(_) {
        return filename.indexOf(_) !== -1;
    }
    if (f.type === 'application/vnd.google-earth.kml+xml' || ext('.kml')) {
        return 'kml';
    }
    if (ext('.gpx')) return 'gpx';
    if (ext('.geojson') || ext('.json')) return 'geojson';
    if (f.type === 'text/csv' || ext('.csv') || ext('.tsv') || ext('.dsv')) {
        return 'dsv';
    }
    if (ext('.xml')) return 'osm';
};


L.DomUtil.add = function (tagName, className, container, content) {
    var el = L.DomUtil.create(tagName, className, container);
    if (content) {
        if (content.nodeType && content.nodeType === 1) {
            el.appendChild(content);
        }
        else {
            el.innerHTML = content;
        }
    }
    return el;
};

L.DomUtil.createFieldset = function (container, legend) {
    var fieldset = L.DomUtil.create('fieldset', 'toggle', container);
    var legendEl = L.DomUtil.add('legend', 'style_options_toggle', fieldset, legend);
    L.DomEvent.on(legendEl, 'click', function () {
        if (L.DomUtil.hasClass(fieldset, 'on')) {
            L.DomUtil.removeClass(fieldset, 'on');
        } else {
            L.DomUtil.addClass(fieldset, 'on');
        }
    });
    return fieldset;
};

L.DomUtil.classIf = function (el, className, bool) {
    if (bool) {
        L.DomUtil.addClass(el, className);
    } else {
        L.DomUtil.removeClass(el, className);
    }
};


L.DomUtil.element = function (what, attrs, parent) {
    var el = document.createElement(what);
    for (var attr in attrs) {
        el[attr] = attrs[attr];
    }
    if (typeof parent !== "undefined") {
        parent.appendChild(el);
    }
    return el;
};


L.DomUtil.before = function (target, el) {
    target.parentNode.insertBefore(el, target);
    return el;
};

L.DomUtil.after = function (target, el)
{
    target.parentNode.insertBefore(el, target.nextSibling);
    return el;
};


/*
* Global events
*/
L.S.Keys = {
    LEFT: 37,
    UP: 38,
    RIGHT: 39,
    DOWN: 40,
    TAB: 9,
    RETURN: 13,
    ESC: 27,
    APPLE: 91,
    SHIFT: 16,
    ALT: 17,
    CTRL: 18
};
L.S._onKeyDown = function (e) {
    if (e.keyCode == L.S.Keys.ESC) {
        L.S.fire('ui:end');
    }
};
L.DomEvent.addListener(document, 'keydown', L.S._onKeyDown, L.S);


L.Storage.Help = L.Class.extend({

    initialize: function (map) {
        this.map = map;
        this.parentContainer = L.DomUtil.create('div', 'storage-help-container', document.body);
        this.overlay = L.DomUtil.create('div', 'storage-help-overlay', this.parentContainer);
        this.box = L.DomUtil.create('div', 'storage-help-box', this.parentContainer);
        this.closeButton = L.DomUtil.add('a', 'storage-close-link', this.box, '&times;');
        this.content = L.DomUtil.create('div', 'storage-help-content', this.box);
        L.DomEvent.on(this.closeButton, 'click', this.hide, this);
        L.DomEvent.addListener(this.parentContainer, 'keydown', this.onKeyDown, this);
    },

    onKeyDown: function (e) {
        var key = e.keyCode,
            ESC = 27;
        if (key == ESC) {
            this.hide();
        }
    },

    show: function () {
        this.content.innerHTML = '';
        for (var i = 0, name; i < arguments.length; i++) {
            name = arguments[i];
            L.DomUtil.add('div', '', this.content, this.resolve(name));
        }
        L.DomUtil.addClass(document.body, 'storage-help-on');
    },

    hide: function () {
        L.DomUtil.removeClass(document.body, 'storage-help-on');
    },

    resolve: function (name) {
        return typeof this[name] === "function" ? this[name]() : this[name];
    },

    button: function (container, entries) {
        var helpButton = L.DomUtil.create('a', 'storage-help-button', container);
        helpButton.href = "#";
        if (entries) {
            L.DomEvent
                .on(helpButton, 'click', L.DomEvent.stop)
                .on(helpButton, 'click', function (e) {
                    var args = typeof entries === "string"? [entries] : entries;
                    this.show.apply(this, args);
                }, this);
        }
        return helpButton;
    },

    edit: function () {
        var container = L.DomUtil.create('div', ''),
            self = this,
            title = L.DomUtil.create('h3', '', container),
            actionsContainer = L.DomUtil.create('ul', 'storage-edit-actions', container);
        var addAction = function (action) {
            var actionContainer = L.DomUtil.add('li', action.className, actionsContainer, action.title);
            L.DomEvent.on(actionContainer, 'click', action.callback, action.context);
            L.DomEvent.on(actionContainer, 'click', self.hide, self);
        };
        title.innerHTML = L._('Where do we go from here?');
        var actions = this.map.getEditActions();
        actions.unshift(
            {
                title: L._('Draw a polyline') + ' (Ctrl+L)',
                className: 'leaflet-draw-draw-polyline',
                callback: function () {this.hide(); this.map._controls.draw.startPolyline();},
                context: this
            },
            {
                title: L._('Draw a polygon') + ' (Ctrl+P)',
                className: 'leaflet-draw-draw-polygon',
                callback: function () {this.hide(); this.map._controls.draw.startPolygone();},
                context: this
            },
            {
                title: L._('Draw a marker') + ' (Ctrl+M)',
                className: 'leaflet-draw-draw-marker',
                callback: function () {this.hide(); this.map._controls.draw.startMarker();},
                context: this
            }
        );
        for (var i = 0; i < actions.length; i++) {
            addAction(actions[i]);
        }
        return container;
    },

    importFormats: function () {
        var container = L.DomUtil.create('div');
        L.DomUtil.add('h3', '', container,'GeojSON');
        L.DomUtil.add('p', '', container, L._('All properties are imported.'));
        L.DomUtil.add('h3', '', container,'GPX');
        L.DomUtil.add('p', '', container, L._('Properties imported:') + 'name, desc');
        L.DomUtil.add('h3', '', container,'KML');
        L.DomUtil.add('p', '', container, L._('Properties imported:') + 'name, description');
        L.DomUtil.add('h3', '', container,'CSV');
        L.DomUtil.add('p', '', container, L._('Comma, tab or semi-colon separated values. SRS WGS84 is implied. Only Point geometries are imported. The import will look at the column headers for any mention of «lat» and «lon» at the begining of the header, case insensitive. All other column are imported as properties.'));
        return container;
    },

    textFormatting: function () {
        var container = L.DomUtil.create('div'),
            title = L.DomUtil.add('h3', '', container, L._('Text formatting')),
            elements = L.DomUtil.create('ul', '', container);
        L.DomUtil.add('li', '', elements, L._('*simple star for italic*'));
        L.DomUtil.add('li', '', elements, L._('**double star for bold**'));
        L.DomUtil.add('li', '', elements, L._('# one hash for main heading'));
        L.DomUtil.add('li', '', elements, L._('## two hashes for second heading'));
        L.DomUtil.add('li', '', elements, L._('### three hashes for third heading'));
        L.DomUtil.add('li', '', elements, L._('Simple link: [[http://example.com]]'));
        L.DomUtil.add('li', '', elements, L._('Link with text: [[http://example.com|text of the link]]'));
        L.DomUtil.add('li', '', elements, L._('Image: {{http://image.url.com}}'));
        L.DomUtil.add('li', '', elements, L._('Image with custom width (in px): {{http://image.url.com|width}}'));
        L.DomUtil.add('li', '', elements, L._('Iframe: {{{http://image.url.com}}}'));
        L.DomUtil.add('li', '', elements, L._('Iframe with custom height (in px): {{{http://image.url.com|height}}}'));
        L.DomUtil.add('li', '', elements, L._('--- for an horizontal rule'));
        return container;
    },

    formatURL: L._('Supported variables that will be dynamically replaced') + ': {bbox}, {lat}, {lng}, {zoom}, {east}, {north}..., {left}, {top}...',
    formatIconURL: L._('You can use feature properties as variables: ex.: with "http://myserver.org/images/{name}.png", the {name} variable will be replaced by the "name" value of each markers.')

});
