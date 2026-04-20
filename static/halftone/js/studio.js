/* TrioStudio · Halftone DTF — UI glue (zoom, drag & drop, export) */
(function () {
    'use strict';

    var MIN_ZOOM = 0.1;
    var MAX_ZOOM = 5.0;
    var STEP = 0.15;

    var state = { zoom: 1.0, done: false };

    function applyZoom() {
        var stage = document.getElementById('ts-stage');
        if (stage) stage.style.setProperty('--zoom', state.zoom);
        var v = document.getElementById('ts-zoom-val');
        if (v) v.textContent = Math.round(state.zoom * 100) + '%';
    }
    function setZoom(z) {
        state.zoom = Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, z));
        applyZoom();
    }

    // Drag & drop upload
    document.addEventListener('dragover', function (e) {
        var dz = e.target.closest('.ts-dropzone');
        if (dz) { e.preventDefault(); dz.classList.add('is-drag'); }
    });
    document.addEventListener('dragleave', function (e) {
        var dz = e.target.closest('.ts-dropzone');
        if (dz) dz.classList.remove('is-drag');
    });
    document.addEventListener('drop', function (e) {
        var dz = e.target.closest('.ts-dropzone');
        if (!dz) return;
        e.preventDefault();
        dz.classList.remove('is-drag');
        var input = document.getElementById('id_original');
        if (input && e.dataTransfer.files.length) {
            input.files = e.dataTransfer.files;
            input.dispatchEvent(new Event('change', { bubbles: true }));
        }
    });
    document.addEventListener('change', function (e) {
        if (e.target.id === 'id_original') {
            var form = document.getElementById('ts-upload-form');
            if (form) form.requestSubmit();
        }
    });

    // Slider live labels
    document.addEventListener('input', function (e) {
        if (e.target.matches('input[type=range]')) {
            var out = document.querySelector('output[data-for="' + e.target.id + '"]');
            if (out) {
                var unit = out.dataset.unit || '';
                var d = parseInt(out.dataset.decimals || '1', 10);
                out.textContent = parseFloat(e.target.value).toFixed(d) + unit;
            }
            markDirty();
        }
    });

    // Segmented controls (shape/dpi) + mark dirty
    document.addEventListener('change', function (e) {
        var t = e.target;
        if (t.matches('.ts-shape-opt input, .ts-dpi-opt input')) {
            document.querySelectorAll('input[name="' + t.name + '"]').forEach(function (r) {
                r.parentElement.classList.toggle('is-on', r.checked);
            });
        }
        if (t.closest('#ts-params-form')) markDirty();
    });

    function markDirty() {
        var applyBtn = document.getElementById('ts-apply-btn');
        if (applyBtn && !applyBtn.disabled) applyBtn.classList.add('is-dirty');
    }

    // When HTMX swaps content into #ts-status, reveal it
    document.addEventListener('htmx:afterSwap', function (e) {
        if (e.detail.target && e.detail.target.id === 'ts-status') {
            var el = e.detail.target;
            el.classList.remove('ts-status--idle');
            el.hidden = false;
        }
    });

    function showStatus(el, html, cls) {
        if (!el) return;
        el.innerHTML = html;
        el.className = 'ts-status ' + (cls || '');
        el.hidden = false;
        if (window.htmx) htmx.process(el);
    }

    function applyParams() {        var applyBtn = document.getElementById('ts-apply-btn');
        var url = applyBtn && applyBtn.dataset.paramsUrl;
        if (!url) return;
        var form = document.getElementById('ts-params-form');
        var statusEl = document.getElementById('ts-status');
        showStatus(statusEl, '<span class="ts-spinner"></span> Aplicando\u2026', 'ts-status--busy');
        if (applyBtn) { applyBtn.disabled = true; applyBtn.classList.remove('is-dirty'); }
        var fd = new FormData(form);
        fetch(url, {
            method: 'POST', body: fd, credentials: 'same-origin',
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
        })
            .then(function (r) { return r.text(); })
            .then(function (html) {
                showStatus(statusEl, html, '');
                if (applyBtn) applyBtn.disabled = false;
                state.done = false;
                var poller = document.getElementById('ts-poller');
                if (poller) htmx.trigger(poller, 'load');
            })
            .catch(function () {
                showStatus(statusEl, '\u2717 Error al aplicar', 'ts-status--err');
                if (applyBtn) applyBtn.disabled = false;
            });
    }

    function getCsrf() {
        var el = document.querySelector('input[name=csrfmiddlewaretoken]');
        return el ? el.value : '';
    }

    // Defaults used by the Reset button (must match model defaults)
    var DEFAULTS = {
        id_knockout_enable: { type: 'checkbox', value: true },
        id_knockout_color:  { type: 'color',    value: '#000000' },
        id_bg_color:        { type: 'color',    value: '#ffffff' },
        id_dot_shape:       { type: 'radio',    value: 'circle' },
        id_dot_size:        { type: 'range',    value: '6' },
        id_dot_angle:       { type: 'range',    value: '45' },
        id_print_width_cm:  { type: 'range',    value: '25' },
        id_export_dpi:      { type: 'radio',    value: '300' },
        id_contrast_boost:  { type: 'range',    value: '1.2' },
        id_blur:            { type: 'range',    value: '0' },
        id_gamma:           { type: 'range',    value: '1' },
        id_gradient_intensity: { type: 'range', value: '0.8' },
        id_brightness:      { type: 'range',    value: '0' },
    };

    function resetForm() {
        Object.keys(DEFAULTS).forEach(function (id) {
            var d = DEFAULTS[id];
            if (d.type === 'radio') {
                var checked = document.querySelector('input[type=radio][value="' + d.value + '"][id^="' + id.replace('id_', '') + '"], input[type=radio][value="' + d.value + '"][name="' + id.replace('id_', '') + '"]');
                // find by name attribute, safer
                var radios = document.querySelectorAll('input[type=radio][name="' + id.replace('id_', '') + '"]');
                radios.forEach(function (r) {
                    r.checked = (r.value === d.value);
                    r.parentElement.classList.toggle('is-on', r.checked);
                });
            } else {
                var el = document.getElementById(id);
                if (!el) return;
                if (d.type === 'checkbox') {
                    el.checked = d.value;
                } else {
                    el.value = d.value;
                    // Update live output label
                    var out = document.querySelector('output[data-for="' + id + '"]');
                    if (out) {
                        var unit = out.dataset.unit || '';
                        var dec  = parseInt(out.dataset.decimals || '1', 10);
                        out.textContent = parseFloat(d.value).toFixed(dec) + unit;
                    }
                }
            }
        });
        // Mark dirty so user knows to click Apply
        markDirty();
    }

    document.addEventListener('click', function (e) {
        // Apply params on demand
        if (e.target.closest('#ts-apply-btn')) {
            applyParams();
            return;
        }

        // Reset sidebar to defaults
        if (e.target.closest('#ts-reset-btn')) {
            resetForm();
            return;
        }

        // Toggle any collapsible section (uses data-target attribute)
        var coll = e.target.closest('.ts-collapsible');
        if (coll) {
            var targetId = coll.dataset.target;
            var body = targetId ? document.getElementById(targetId) : null;
            var chev = coll.querySelector('.ts-chev');
            if (body) body.hidden = !body.hidden;
            if (chev) chev.textContent = body && !body.hidden ? '\u25B2' : '\u25BC';
            return;
        }

        // Replace image
        if (e.target.closest('#ts-replace-btn')) {
            var delBtn = document.getElementById('ts-delete-btn');
            if (delBtn) {
                delBtn.removeAttribute('hx-confirm');
                htmx.trigger(delBtn, 'click');
            }
            var tries = 0;
            var t = setInterval(function () {
                tries++;
                var input = document.getElementById('id_original');
                if (input) { clearInterval(t); input.click(); }
                else if (tries > 40) { clearInterval(t); }
            }, 80);
            return;
        }

        // Export (manual fetch so it never gets swallowed by the params form)
        var exportBtn = e.target.closest('#ts-export-btn');
        if (exportBtn) {
            var url = exportBtn.dataset.exportUrl;
            if (!url) return;
            var statusEl = document.getElementById('ts-status');
            showStatus(statusEl, '<span class="ts-spinner"></span> Preparando exportaci\u00f3n\u2026', 'ts-status--busy');
            exportBtn.disabled = true;
            var fd = new FormData();
            fd.append('csrfmiddlewaretoken', getCsrf());
            fetch(url, {
                method: 'POST', body: fd, credentials: 'same-origin',
                headers: { 'HX-Request': 'true', 'X-Requested-With': 'XMLHttpRequest' },
            })
                .then(function (r) { return r.text(); })
                .then(function (html) {
                    showStatus(statusEl, html, '');
                    exportBtn.disabled = false;
                })
                .catch(function () {
                    showStatus(statusEl, '\u2717 Error al exportar', 'ts-status--err');
                    exportBtn.disabled = false;
                });
            return;
        }

        // Zoom
        if (e.target.closest('#ts-zoom-in'))   setZoom(state.zoom + STEP);
        if (e.target.closest('#ts-zoom-out'))  setZoom(state.zoom - STEP);
        if (e.target.closest('#ts-zoom-undo')) setZoom(1.0);
        if (e.target.closest('#ts-zoom-fit'))  setZoom(1.0);
    });

    var canvasWrap = document.querySelector('.ts-canvas-wrap');
    if (canvasWrap) {
        canvasWrap.addEventListener('wheel', function (e) {
            if (!document.getElementById('ts-stage')) return;
            e.preventDefault();
            var delta = e.deltaY < 0 ? STEP : -STEP;
            setZoom(state.zoom + delta);
        }, { passive: false });
    }

    window.shouldPoll = function () { return !state.done; };

    window.TrioStudio = {
        onStageReady: function () {
            state.zoom = 1.0;
            state.done = false;
            applyZoom();
            var a = document.getElementById('ts-canvas-actions');
            var z = document.getElementById('ts-zoombar');
            if (a) a.hidden = false;
            if (z) z.hidden = false;
        },
        onPreviewReady: function () { state.done = true; }
    };
})();
