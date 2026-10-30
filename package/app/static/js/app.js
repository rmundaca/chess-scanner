'use strict';

/* ------------------------------------------------------------------ i18n */

const I18N = {
    es: {
        locale: 'es-ES',
        appName: 'Chess Scanner',
        tabScan: 'Escanear', tabHistory: 'Historial',
        settings: 'Ajustes', close: 'Cerrar', cancel: 'Cancelar', save: 'Guardar', delete: 'Eliminar',
        pickTitle: 'Escanea un diagrama',
        pickText: 'Haz una foto al diagrama del libro, ajusta las esquinas y coloca las piezas para obtener el FEN.',
        takePhoto: 'Hacer foto', chooseImage: 'Elegir imagen',
        pasteHint: 'En el ordenador también puedes pegar una captura con Ctrl+V.',
        cornersTitle: 'Esquinas del tablero',
        cornersHint: 'Arrastra los 4 puntos hasta las esquinas de las casillas, sin el marco ni las coordenadas.',
        rotate: 'Girar', discard: 'Descartar', continue: 'Continuar', adjustCorners: 'Ajustar esquinas',
        boardTitle: 'Tablero', viewPhoto: 'Foto', viewDiagram: 'Diagrama',
        paletteHint: 'Elige una pieza y toca las casillas. Tocar otra vez la quita.',
        eraser: 'Borrar', clearBoard: 'Vaciar', clearBoardMsg: 'Se quitarán todas las piezas del tablero.',
        toMove: 'Juegan', white: 'Blancas', black: 'Negras',
        bottom: 'Abajo están', castling: 'Enroques', noCastling: 'Ninguno posible con esta posición.',
        fen: 'FEN', copy: 'Copiar', copied: 'FEN copiado', copyFailed: 'No se pudo copiar: selecciona el texto a mano.',
        lichess: 'Lichess', chesscom: 'Chess.com',
        saveScan: 'Guardar escaneo', updateScan: 'Guardar cambios', newScan: 'Nuevo escaneo', newShort: 'Nuevo',
        scanTitle: 'Nombre (opcional)', scanTitlePh: 'Libro, página, diagrama…',
        saved: 'Escaneo guardado', updated: 'Cambios guardados', deleted: 'Escaneo eliminado',
        deleteScan: 'Eliminar escaneo', deleteScanMsg: 'Se borrarán la posición y sus imágenes.',
        discardScan: 'Descartar escaneo', discardScanMsg: 'Hay cambios sin guardar que se perderán.',
        historyEmptyTitle: 'Sin escaneos guardados',
        historyEmptyText: 'Los diagramas que guardes aparecerán aquí y servirán para entrenar el reconocimiento automático.',
        savedScans: 'Guardados ({n})', untitled: 'Diagrama {id}', exportData: 'Exportar',
        whiteToMove: 'Juegan blancas', blackToMove: 'Juegan negras',
        recognizing: 'Reconociendo piezas…',
        doubtSquares: 'Revisa las casillas marcadas ({n}): el reconocimiento no está seguro.',
        flipGuess: 'Parece que el diagrama tiene las negras abajo. Compruébalo en FEN.',
        recognizeFailed: 'No se pudo reconocer la posición: coloca las piezas a mano.',
        model: 'Reconocimiento', modelNone: 'No hay modelo: las piezas se colocan a mano.',
        modelInfo: 'Modelo {id} del {date}', modelBundled: 'De fábrica', modelUploaded: 'Subido',
        modelAcc: 'Acierto en fotos reales: {acc}',
        uploadModel: 'Subir modelo', uploadModelHint: 'Elige a la vez model.json y model.bin (training/out/ en el PC).',
        resetModel: 'Volver al de fábrica', modelSaved: 'Modelo actualizado', modelResetDone: 'Modelo de fábrica restaurado',
        warn: {
            empty: 'El tablero está vacío.',
            whiteKing: 'Debe haber exactamente un rey blanco.',
            blackKing: 'Debe haber exactamente un rey negro.',
            pawnRank: 'Hay peones en la primera u octava fila.',
            tooMany: 'Algún bando tiene más de 16 piezas.',
        },
        pieceNames: {
            K: 'rey blanco', Q: 'dama blanca', R: 'torre blanca', B: 'alfil blanco', N: 'caballo blanco', P: 'peón blanco',
            k: 'rey negro', q: 'dama negra', r: 'torre negra', b: 'alfil negro', n: 'caballo negro', p: 'peón negro',
        },
        theme: 'Tema', themeOpt: { system: 'Sistema', light: 'Claro', dark: 'Oscuro' },
        themeHint: 'Se guarda en este dispositivo.',
        language: 'Idioma', version: 'Versión {v}',
        err: {
            network: 'No se pudo contactar con el servidor.',
            not_found: 'Ya no existe.',
            invalid_fen: 'La posición no es válida.',
            invalid_image: 'La imagen no es válida.',
            image_too_large: 'La imagen es demasiado grande.',
            invalid_corners: 'Las esquinas no son válidas.',
            storage_error: 'No se pudo guardar en el NAS.',
            image_load: 'No se pudo abrir la imagen.',
            invalid_model: 'El modelo no es válido o no corresponde a esta versión de la app.',
            model_missing: 'No hay ningún modelo instalado.',
            model_files: 'Elige los dos ficheros: model.json y model.bin.',
            invalid_prediction: 'La propuesta del reconocimiento no es válida.',
            generic: 'Algo salió mal. Inténtalo de nuevo.',
        },
    },
    en: {
        locale: 'en-GB',
        appName: 'Chess Scanner',
        tabScan: 'Scan', tabHistory: 'History',
        settings: 'Settings', close: 'Close', cancel: 'Cancel', save: 'Save', delete: 'Delete',
        pickTitle: 'Scan a diagram',
        pickText: 'Take a photo of the book diagram, adjust the corners and place the pieces to get the FEN.',
        takePhoto: 'Take photo', chooseImage: 'Choose image',
        pasteHint: 'On a computer you can also paste a screenshot with Ctrl+V.',
        cornersTitle: 'Board corners',
        cornersHint: 'Drag the 4 points to the corners of the squares, leaving out the frame and coordinates.',
        rotate: 'Rotate', discard: 'Discard', continue: 'Continue', adjustCorners: 'Adjust corners',
        boardTitle: 'Board', viewPhoto: 'Photo', viewDiagram: 'Diagram',
        paletteHint: 'Pick a piece and tap the squares. Tap again to remove it.',
        eraser: 'Erase', clearBoard: 'Clear', clearBoardMsg: 'All pieces will be removed from the board.',
        toMove: 'To move', white: 'White', black: 'Black',
        bottom: 'At the bottom', castling: 'Castling', noCastling: 'None possible in this position.',
        fen: 'FEN', copy: 'Copy', copied: 'FEN copied', copyFailed: 'Could not copy: select the text manually.',
        lichess: 'Lichess', chesscom: 'Chess.com',
        saveScan: 'Save scan', updateScan: 'Save changes', newScan: 'New scan', newShort: 'New',
        scanTitle: 'Name (optional)', scanTitlePh: 'Book, page, diagram…',
        saved: 'Scan saved', updated: 'Changes saved', deleted: 'Scan deleted',
        deleteScan: 'Delete scan', deleteScanMsg: 'The position and its images will be deleted.',
        discardScan: 'Discard scan', discardScanMsg: 'Unsaved changes will be lost.',
        historyEmptyTitle: 'No saved scans',
        historyEmptyText: 'Diagrams you save will show up here and will help train automatic recognition.',
        savedScans: 'Saved ({n})', untitled: 'Diagram {id}', exportData: 'Export',
        whiteToMove: 'White to move', blackToMove: 'Black to move',
        recognizing: 'Recognising pieces…',
        doubtSquares: 'Check the highlighted squares ({n}): recognition is not sure about them.',
        flipGuess: 'Black seems to be at the bottom of this diagram. Check it under FEN.',
        recognizeFailed: 'Could not recognise the position: place the pieces by hand.',
        model: 'Recognition', modelNone: 'No model installed: pieces are placed by hand.',
        modelInfo: 'Model {id} from {date}', modelBundled: 'Built-in', modelUploaded: 'Uploaded',
        modelAcc: 'Accuracy on real photos: {acc}',
        uploadModel: 'Upload model', uploadModelHint: 'Pick model.json and model.bin together (training/out/ on the PC).',
        resetModel: 'Back to built-in', modelSaved: 'Model updated', modelResetDone: 'Built-in model restored',
        warn: {
            empty: 'The board is empty.',
            whiteKing: 'There must be exactly one white king.',
            blackKing: 'There must be exactly one black king.',
            pawnRank: 'There are pawns on the first or eighth rank.',
            tooMany: 'One side has more than 16 pieces.',
        },
        pieceNames: {
            K: 'white king', Q: 'white queen', R: 'white rook', B: 'white bishop', N: 'white knight', P: 'white pawn',
            k: 'black king', q: 'black queen', r: 'black rook', b: 'black bishop', n: 'black knight', p: 'black pawn',
        },
        theme: 'Theme', themeOpt: { system: 'System', light: 'Light', dark: 'Dark' },
        themeHint: 'Saved on this device.',
        language: 'Language', version: 'Version {v}',
        err: {
            network: 'Could not reach the server.',
            not_found: 'It no longer exists.',
            invalid_fen: 'The position is not valid.',
            invalid_image: 'The image is not valid.',
            image_too_large: 'The image is too large.',
            invalid_corners: 'The corners are not valid.',
            storage_error: 'Could not save on the NAS.',
            image_load: 'Could not open the image.',
            invalid_model: 'The model is not valid or does not match this app version.',
            model_missing: 'No model is installed.',
            model_files: 'Pick both files: model.json and model.bin.',
            invalid_prediction: 'The recognition result is not valid.',
            generic: 'Something went wrong. Please try again.',
        },
    },
};

const STORE_PREFIX = 'cs_';
const THEME_COLORS = { dark: '#0b0f19', light: '#eef1f6' };
const PHOTO_MAX_SIDE = 1600;   // stored photo (and base for corner adjustment)
const BOARD_SIZE = 512;        // rectified board: 64 px per square
const DOUBT_CONF = 0.85;       // below this, the square is flagged for review

const S = {
    lang: readStorage('lang') || (navigator.language || 'es').slice(0, 2),
    tab: 'scan',
    scans: [],
    version: '',
    model: null,     // /api/model (null = no model: everything by hand)
    busy: false,
    busyText: '',
    scan: null,      // scan in progress (see newScan)
    brush: 'P',      // piece selected in the palette ('' = erase)
    boardView: readStorage('boardView') === 'diagram' ? 'diagram' : 'photo',
    fenView: false,  // while editing: position settings and FEN instead of the board
};

/* ------------------------------------------------------------- helpers */

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

function readStorage(key) {
    try { return localStorage.getItem(STORE_PREFIX + key); } catch (e) { return null; }
}

function writeStorage(key, value) {
    try { localStorage.setItem(STORE_PREFIX + key, value); } catch (e) { /* private mode */ }
}

function t(key, vars) {
    const dict = I18N[S.lang] || I18N.es;
    let value = key.split('.').reduce((o, k) => (o == null ? undefined : o[k]), dict);
    if (value === undefined) value = key;
    if (vars && typeof value === 'string') {
        value = value.replace(/\{(\w+)\}/g, (_, k) => (vars[k] ?? ''));
    }
    return value;
}

function esc(value) {
    return String(value ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

async function api(path, { method = 'GET', body } = {}) {
    let res;
    try {
        res = await fetch(path, {
            method,
            headers: body ? { 'Content-Type': 'application/json' } : undefined,
            body: body ? JSON.stringify(body) : undefined,
        });
    } catch (e) {
        throw new Error('network');
    }
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'generic');
    return data;
}

function errText(e) {
    return (I18N[S.lang] || I18N.es).err[e && e.message] || t('err.generic');
}

function toast(message, kind = 'ok') {
    const el = document.createElement('div');
    el.className = `toast ${kind}`;
    el.textContent = message;
    $('#toasts').appendChild(el);
    setTimeout(() => el.classList.add('hide'), 3200);
    setTimeout(() => el.remove(), 3600);
}

function fmtDate(iso, opts = { day: 'numeric', month: 'short', year: 'numeric' }) {
    return new Date(iso).toLocaleDateString(t('locale'), opts);
}

function cssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

// Clipboard: the modern API requires HTTPS; on the LAN (HTTP) execCommand is used
async function copyText(text) {
    try {
        if (navigator.clipboard && window.isSecureContext) {
            await navigator.clipboard.writeText(text);
            return true;
        }
    } catch (e) { /* fall back to the classic method */ }
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.setAttribute('readonly', '');
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    ta.setSelectionRange(0, text.length);
    let ok = false;
    try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
    ta.remove();
    return ok;
}

const CHEVRON = '<svg class="chev" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 6l6 6-6 6"/></svg>';
const ICON_ERASER = '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 20H9L4.5 15.5a2 2 0 0 1 0-2.8l8.7-8.7a2 2 0 0 1 2.8 0l3.5 3.5a2 2 0 0 1 0 2.8L12 18"/><path d="M8.5 9.5l6 6"/></svg>';
const ICON_CAMERA = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 8h3l2-3h6l2 3h3a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1z"/><circle cx="12" cy="13.5" r="3.5"/></svg>';
const ICON_IMAGE = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="9" cy="10" r="2"/><path d="M21 16l-5-5-9 9"/></svg>';

/* ---------------------------------------------------------------- pieces */

// Custom pieces (geometric, viewBox 45x45). "pb" = body, "pd" = detail in contrast colour.
const PIECE_SHAPES = {
    p: [
        ['pb', '<circle cx="22.5" cy="13" r="5.2"/>'],
        ['pb', '<path d="M18.2 20h8.6l2.6 12.5h-13.8z"/>'],
        ['pb', '<rect x="16.5" y="18.2" width="12" height="3" rx="1.5"/>'],
        ['pb', '<rect x="11.5" y="32.5" width="22" height="6" rx="2"/>'],
    ],
    r: [
        ['pb', '<path d="M11.5 7.5h4.6v3.6h3.5V7.5h5.8v3.6h3.5V7.5h4.6v8.5h-22z"/>'],
        ['pb', '<path d="M14.6 16h15.8l1.4 16.5H13.2z"/>'],
        ['pb', '<rect x="10.5" y="32.5" width="24" height="6" rx="2"/>'],
        ['pd', '<path d="M14.8 19.5h15.4M13.9 29h17.2"/>'],
    ],
    b: [
        ['pb', '<circle cx="22.5" cy="6.6" r="2.6"/>'],
        ['pb', '<path d="M22.5 9.2c-5.4 4-8.6 8.8-8.6 13.6 0 3.6 1.9 6.1 3.8 7.4h9.6c1.9-1.3 3.8-3.8 3.8-7.4 0-4.8-3.2-9.6-8.6-13.6z"/>'],
        ['pb', '<rect x="15.5" y="29.5" width="14" height="3.4" rx="1.5"/>'],
        ['pb', '<rect x="11.5" y="32.5" width="22" height="6" rx="2"/>'],
        ['pd', '<path d="M25.6 14.2l-5.4 7.2M19.6 25.6h5.8"/>'],
    ],
    n: [
        ['pb', '<path d="M14.5 32.5c.4-3.6 2.2-6.4 4.8-8.6l-3.2 1.2c-1.6.6-3.2.1-4.1-1.2l-1.4-2.1c-.7-1-.5-2.3.3-3.2l7.4-7.5 1.1-4.6 3.3 3.6 2.6-3.2.9 4.3c5.6 2.8 8.4 8.6 8.4 15.6v5.7z"/>'],
        ['pb', '<rect x="11.5" y="32.5" width="22" height="6" rx="2"/>'],
        ['pd', '<circle class="dot" cx="19.4" cy="15.4" r="1.5"/>'],
    ],
    q: [
        ['pb', '<path d="M12.4 31L9.3 14.4l7.1 9 .3-12.4 5.8 11.4 5.8-11.4.3 12.4 7.1-9L32.6 31z"/>'],
        ['pb', '<circle cx="9" cy="13" r="2.3"/><circle cx="16.6" cy="9.8" r="2.3"/><circle cx="22.5" cy="8.6" r="2.3"/><circle cx="28.4" cy="9.8" r="2.3"/><circle cx="36" cy="13" r="2.3"/>'],
        ['pb', '<rect x="10.5" y="32.5" width="24" height="6" rx="2"/>'],
        ['pd', '<path d="M13 28h19"/>'],
    ],
    k: [
        ['pb', '<path d="M21.1 3.5h2.8v3h3v2.8h-3v4.4h-2.8V9.3h-3V6.5h3z"/>'],
        ['pb', '<path d="M12.6 31c-3.4-5.6-3-13 2.8-14.6 3.6-1 6.4.9 7.1 3.7.7-2.8 3.5-4.7 7.1-3.7 5.8 1.6 6.2 9 2.8 14.6z"/>'],
        ['pb', '<path d="M19.2 18.6c.6-2.6 1.8-4.3 3.3-5 1.5.7 2.7 2.4 3.3 5l-3.3 3.4z"/>'],
        ['pb', '<rect x="10.5" y="32.5" width="24" height="6" rx="2"/>'],
        ['pd', '<path d="M13.4 28h18.2M22.5 22v6"/>'],
    ],
};
const PIECE_SVG = Object.fromEntries(Object.entries(PIECE_SHAPES).map(([k, shapes]) =>
    [k, shapes.map(([cls, svg]) => `<g class="${cls}">${svg}</g>`).join('')]));

function pieceSvg(ch) {
    const white = ch === ch.toUpperCase();
    return `<svg class="pc ${white ? 'w' : 'k'}" viewBox="0 0 45 45" aria-hidden="true">${PIECE_SVG[ch.toLowerCase()]}</svg>`;
}

/* ------------------------------------------------------------ position */

// cells: 64 squares in visual order (top row first, as seen in the photo).
// With flipped (black at the bottom) the FEN order is reversed.
function boardArray(sc) {
    return sc.flipped ? sc.cells.slice().reverse() : sc.cells;
}

function cellsFromPlacement(placement, flipped) {
    const arr = [];
    for (const ch of placement.replace(/\//g, '')) {
        if (/\d/.test(ch)) for (let i = 0; i < Number(ch); i++) arr.push('');
        else arr.push(ch);
    }
    return flipped ? arr.reverse() : arr;
}

function castlingRights(arr) {
    const rights = [];
    if (arr[60] === 'K') {
        if (arr[63] === 'R') rights.push('K');
        if (arr[56] === 'R') rights.push('Q');
    }
    if (arr[4] === 'k') {
        if (arr[7] === 'r') rights.push('k');
        if (arr[0] === 'r') rights.push('q');
    }
    return rights;
}

function position(sc) {
    const arr = boardArray(sc);
    const ranks = [];
    for (let r = 0; r < 8; r++) {
        let rank = '';
        let empty = 0;
        for (let c = 0; c < 8; c++) {
            const ch = arr[r * 8 + c];
            if (!ch) { empty++; continue; }
            if (empty) { rank += empty; empty = 0; }
            rank += ch;
        }
        ranks.push(empty ? rank + empty : rank);
    }
    const placement = ranks.join('/');
    const avail = castlingRights(arr);
    const castling = avail.filter(c => !sc.castleOff.includes(c)).join('') || '-';
    return { arr, placement, avail, castling, fen: `${placement} ${sc.side} ${castling} - 0 1` };
}

function warnings(arr) {
    const count = ch => arr.filter(x => x === ch).length;
    const out = [];
    if (arr.every(x => !x)) return ['empty'];
    if (count('K') !== 1) out.push('whiteKing');
    if (count('k') !== 1) out.push('blackKing');
    if ([...arr.slice(0, 8), ...arr.slice(56)].some(x => x === 'P' || x === 'p')) out.push('pawnRank');
    const white = arr.filter(x => x && x === x.toUpperCase()).length;
    const black = arr.filter(x => x && x === x.toLowerCase()).length;
    if (white > 16 || black > 16) out.push('tooMany');
    return out;
}

// Likely orientation of a position in visual order: pawns advance towards the opponent and kings
// tend to stay on their own side. Only suggests "black at the bottom" with clear evidence.
function guessFlipped(cells) {
    let score = 0;
    cells.forEach((ch, i) => {
        const r = (i >> 3) - 3.5;   // > 0: bottom half
        if (ch === 'P') score += r;
        else if (ch === 'p') score -= r;
        else if (ch === 'K') score += r / 2;
        else if (ch === 'k') score -= r / 2;
    });
    return score <= -3;
}

function lichessUrl(fen, flipped) {
    return `https://lichess.org/analysis/standard/${fen.replace(/ /g, '_')}${flipped ? '?color=black' : ''}`;
}

function chesscomUrl(fen, flipped) {
    return `https://www.chess.com/analysis?fen=${encodeURIComponent(fen)}${flipped ? '&flip=true' : ''}`;
}

/* --------------------------------------------------------------- sheet */

function openSheet(title, html, onMount) {
    const panel = $('.sheet-panel');
    panel.style.transform = '';
    panel.classList.remove('settle', 'dragging');
    $('#sheetTitle').textContent = title;
    $('#sheetBody').innerHTML = html;
    $('#sheet').hidden = false;
    document.body.classList.add('no-scroll');
    if (onMount) onMount($('#sheetBody'));
}

function closeSheet() {
    $('#sheet').hidden = true;
    $('#sheetBody').innerHTML = '';
    document.body.classList.remove('no-scroll');
}

function confirmSheet(title, message, okLabel, onOk) {
    openSheet(title, `
        <p class="muted">${esc(message)}</p>
        <div class="actions">
            <button type="button" class="btn ghost" data-close>${t('cancel')}</button>
            <button type="button" class="btn danger" id="confirmOk">${esc(okLabel)}</button>
        </div>`, body => {
        $('#confirmOk', body).onclick = async e => {
            e.target.disabled = true;
            await onOk();
        };
    });
}

/* -------------------------------------------------------------- loading */

async function loadAll() {
    const [health, scans, model] = await Promise.allSettled([api('/api/health'), api('/api/scans'), api('/api/model')]);
    if (health.status === 'fulfilled') S.version = health.value.version;
    if (scans.status === 'fulfilled') S.scans = scans.value;
    else toast(errText(scans.reason), 'error');
    if (model.status === 'fulfilled') {
        S.model = model.value;
        loadNet().catch(() => {});  // download weights now, while the photo is being taken
    }
    render();
}

// Net ready for Vision.classify; downloaded once per model (the URL carries the id, immutable cache)
let netCache = { id: null, promise: null };

function loadNet() {
    const info = S.model;
    if (!info) return Promise.resolve(null);
    if (netCache.id !== info.id) {
        const promise = fetch(`/api/model/weights?v=${encodeURIComponent(info.id)}`)
            .then(res => {
                if (!res.ok) throw new Error('model_missing');
                return res.arrayBuffer();
            })
            .then(buf => Vision.createNet(info, buf));
        promise.catch(() => { if (netCache.promise === promise) netCache = { id: null, promise: null }; });
        netCache = { id: info.id, promise };
    }
    return netCache.promise;
}

// Proposes the position of the rectified board. Without a model, or on failure, the board is left as is.
async function recognize(sc) {
    const net = await loadNet();
    if (!net) return;
    const result = await Vision.classify(net, Vision.boardInput(sc.board));
    sc.cells = result.map(r => r.piece);
    sc.doubt = result.map((r, i) => (r.conf < DOUBT_CONF ? i : -1)).filter(i => i >= 0);
    sc.predicted = sc.cells.map(ch => ch || '.').join('');
    sc.modelId = net.id;
    sc.flipGuess = guessFlipped(sc.cells);
    sc.flipped = sc.flipGuess;
}

async function reloadScans() {
    try {
        S.scans = await api('/api/scans');
    } catch (err) {
        toast(errText(err), 'error');
    }
    render();
}

function setLang(lang, rerender = true) {
    S.lang = I18N[lang] ? lang : 'es';
    document.documentElement.lang = S.lang;
    writeStorage('lang', S.lang);
    if (rerender) render();
}

/* ------------------------------------------------------------- rendering */

const TABS = {
    scan: { title: 'tabScan', view: renderScan },
    history: { title: 'tabHistory', view: renderHistory },
};

const BRAND_HTML = $('#brand').innerHTML;

function render() {
    const tab = TABS[S.tab] || TABS.scan;
    const title = t(tab.title);
    // Editing the board: bar with inline title and scan actions, no large title
    const sc = S.tab === 'scan' && !S.busy && S.scan && S.scan.step === 'edit' ? S.scan : null;
    $('#topbar').classList.toggle('inline', !!sc);
    $('#smallTitle').textContent = sc && sc.title ? sc.title : title;
    $('#smallTitle').setAttribute('aria-hidden', String(!sc));
    $('#brand').innerHTML = sc
        ? `<button type="button" class="btn small ghost" data-action="new-scan">${sc.id ? t('newShort') : t('discard')}</button>`
        : BRAND_HTML;
    $('#barActions').innerHTML = sc
        ? `<button type="button" class="btn small primary" data-action="save-scan"${sc.id && !sc.dirty ? ' disabled' : ''}>${t('save')}</button>`
        : '';
    $('#settingsBtn').hidden = !!sc;
    $('#settingsBtn').setAttribute('aria-label', t('settings'));
    $$('#tabs .tab').forEach(b => {
        $('.tab-label', b).textContent = t(TABS[b.dataset.tab].title);
        b.setAttribute('aria-selected', String(b.dataset.tab === S.tab));
    });
    $('#view').innerHTML = `${sc ? '' : `<h1 class="large-title">${esc(title)}</h1>`}${tab.view()}`;
    if (S.tab === 'scan' && S.scan && S.scan.step === 'corners') setupCorners();
}

function renderScan() {
    if (S.busy) return `<div class="loading"><span class="spinner"></span>${S.busyText ? `<p class="muted">${esc(S.busyText)}</p>` : ''}</div>`;
    if (!S.scan) return renderPick();
    return S.scan.step === 'corners' ? renderCorners() : renderEdit();
}

function renderPick() {
    return `
        <section class="empty">
            <img src="/static/icon-192.png" alt="" width="72" height="72">
            <h1>${t('pickTitle')}</h1>
            <p class="muted">${t('pickText')}</p>
            <label class="btn primary big">${ICON_CAMERA}${t('takePhoto')}
                <input type="file" accept="image/*" capture="environment" data-file hidden></label>
            <label class="btn ghost">${ICON_IMAGE}${t('chooseImage')}
                <input type="file" accept="image/*" data-file hidden></label>
            <p class="hint">${t('pasteHint')}</p>
        </section>`;
}

function renderCorners() {
    return `
        <section class="card">
            <div class="card-head"><h2>${t('cornersTitle')}</h2></div>
            <div class="corner-box"><canvas id="cornerCanvas" class="corner-canvas"></canvas></div>
            <p class="hint">${t('cornersHint')}</p>
            <div class="actions spread">
                <button type="button" class="btn ghost" data-action="rotate">${t('rotate')}</button>
                <span class="actions-group">
                    <button type="button" class="btn ghost" data-action="discard">${t('discard')}</button>
                    <button type="button" class="btn primary" data-action="to-edit">${t('continue')}</button>
                </span>
            </div>
        </section>`;
}

function renderBoard(sc) {
    const files = sc.flipped ? 'hgfedcba' : 'abcdefgh';
    const rank = r => (sc.flipped ? r + 1 : 8 - r);
    const photo = S.boardView === 'photo';
    const squares = sc.cells.map((ch, i) => {
        const r = i >> 3;
        const c = i & 7;
        const label = files[c] + rank(r) + (ch ? `, ${t(`pieceNames.${ch}`)}` : '');
        const piece = ch ? (photo ? `<span class="badge">${pieceSvg(ch)}</span>` : pieceSvg(ch)) : '';
        const doubt = sc.doubt.includes(i) ? ' doubt' : '';
        return `<button type="button" class="sq ${(r + c) % 2 ? 'd' : 'l'}${doubt}" data-sq="${i}" aria-label="${esc(label)}">${piece}</button>`;
    }).join('');
    const bg = photo ? ` style="background-image:url('${esc(sc.boardUrl)}')"` : '';
    return `
        <div class="board-wrap">
            <div class="ranks">${[0, 1, 2, 3, 4, 5, 6, 7].map(r => `<span>${rank(r)}</span>`).join('')}</div>
            <div class="board ${photo ? 'photo' : 'diagram'}"${bg}>${squares}</div>
            <span></span>
            <div class="files">${files.split('').map(f => `<span>${f}</span>`).join('')}</div>
        </div>`;
}

function renderPalette() {
    const chip = (value, inner, label) => `<button type="button" class="pchip${S.brush === value ? ' on' : ''}" data-brush="${value}" aria-label="${esc(label)}" aria-pressed="${S.brush === value}">${inner}</button>`;
    const pieces = 'KQRBNPkqrbnp'.split('').map(ch => chip(ch, pieceSvg(ch), t(`pieceNames.${ch}`)));
    return `<div class="palette">${pieces.slice(0, 6).join('')}${chip('', ICON_ERASER, t('eraser'))}${pieces.slice(6).join('')}</div>`;
}

const viewChips = (items, attr, current) => `<div class="chips">${items.map(([value, label]) =>
    `<button type="button" class="chip${value === current ? ' on' : ''}" ${attr}="${value}">${esc(label)}</button>`).join('')}</div>`;

function renderEdit() {
    const sc = S.scan;
    const warns = warnings(position(sc).arr);
    const leftAction = sc.id
        ? `<button type="button" class="btn small ghost danger-text" data-action="delete-scan">${t('delete')}</button>`
        : sc.photo ? `<button type="button" class="btn small ghost" data-action="adjust-corners">${t('adjustCorners')}</button>` : '<span></span>';
    return `
        ${sc.doubt.length ? `<div class="banner"><p>${esc(t('doubtSquares', { n: sc.doubt.length }))}</p></div>` : ''}
        ${sc.flipGuess ? `<div class="banner"><p>${t('flipGuess')}</p></div>` : ''}
        ${warns.length ? `<div class="banner warn"><p>${warns.map(w => esc(t(`warn.${w}`))).join('<br>')}</p></div>` : ''}
        <section class="card editor" aria-label="${esc(t('boardTitle'))}">
            <div class="card-head">
                ${viewChips([['photo', t('viewPhoto')], ['diagram', t('viewDiagram')], ['fen', t('fen')]], 'data-view', S.fenView ? 'fen' : S.boardView)}
            </div>
            ${S.fenView ? renderFen(sc) : `${renderBoard(sc)}${renderPalette()}<p class="hint">${t('paletteHint')}</p>`}
            <div class="actions spread">
                ${leftAction}
                ${S.fenView ? '' : `<button type="button" class="btn small ghost" data-action="clear-board">${t('clearBoard')}</button>`}
            </div>
        </section>`;
}

// FEN view: position data not derived from the board, plus the resulting code
function renderFen(sc) {
    const pos = position(sc);
    const castling = pos.avail.length
        ? `<div class="chips">${pos.avail.map(c => `<button type="button" class="chip${sc.castleOff.includes(c) ? '' : ' on'}" data-castle="${c}">${c === c.toUpperCase() ? t('white') : t('black')} ${c.toLowerCase() === 'k' ? 'O-O' : 'O-O-O'}</button>`).join('')}</div>`
        : `<p class="hint">${t('noCastling')}</p>`;
    return `
        <div class="fen-view">
            <h3>${t('toMove')}</h3>
            ${viewChips([['w', t('white')], ['b', t('black')]], 'data-side', sc.side)}
            <h3>${t('bottom')}</h3>
            ${viewChips([['0', t('white')], ['1', t('black')]], 'data-flip', sc.flipped ? '1' : '0')}
            <h3>${t('castling')}</h3>
            ${castling}
            <h3>${t('fen')}</h3>
            <input class="fen" id="fenField" readonly value="${esc(pos.fen)}" aria-label="${t('fen')}">
            <div class="actions">
                <a class="btn small ghost" href="${esc(lichessUrl(pos.fen, sc.flipped))}" target="_blank" rel="noopener">${t('lichess')}</a>
                <a class="btn small ghost" href="${esc(chesscomUrl(pos.fen, sc.flipped))}" target="_blank" rel="noopener">${t('chesscom')}</a>
                <button type="button" class="btn small primary" data-action="copy-fen">${t('copy')}</button>
            </div>
        </div>`;
}

function renderHistory() {
    if (!S.scans.length) {
        return `
            <section class="empty">
                <img src="/static/icon-192.png" alt="" width="72" height="72">
                <h1>${t('historyEmptyTitle')}</h1>
                <p class="muted">${t('historyEmptyText')}</p>
                <button type="button" class="btn primary big" data-action="goto-scan">${t('newScan')}</button>
            </section>`;
    }
    return `
        <section class="card">
            <div class="card-head">
                <h2>${esc(t('savedScans', { n: S.scans.length }))}</h2>
                <a class="btn small ghost" href="/api/scans/export" download>${t('exportData')}</a>
            </div>
            <div class="rows">${S.scans.map(scanRow).join('')}</div>
        </section>`;
}

function scanRow(s) {
    return `
        <button type="button" class="row" data-scan="${s.id}">
            <img class="thumb" src="/api/scans/${s.id}/board.jpg" alt="" width="48" height="48" loading="lazy">
            <span class="row-main">
                <span class="row-title">${esc(s.title || t('untitled', { id: s.id }))}</span>
                <span class="row-meta">${esc(fmtDate(s.created_at))}
                    <span class="tag">${t(s.side === 'w' ? 'whiteToMove' : 'blackToMove')}</span></span>
            </span>
            ${CHEVRON}
        </button>`;
}

/* --------------------------------------------------------------- scan */

function newScan(photo) {
    // Initial corners: centred square at 80 % of the shorter side
    const side = Math.min(photo.width, photo.height) * 0.8;
    const x0 = (photo.width - side) / 2;
    const y0 = (photo.height - side) / 2;
    return {
        id: null,
        step: 'corners',
        photo,
        corners: [[x0, y0], [x0 + side, y0], [x0 + side, y0 + side], [x0, y0 + side]],
        board: null,
        boardUrl: '',
        cells: Array(64).fill(''),
        side: 'w',
        flipped: false,
        castleOff: [],
        title: '',
        dirty: false,
        edited: false,     // user already touched squares: don't re-recognize when corners are readjusted
        doubt: [],         // low-confidence squares pending review
        predicted: null,   // model proposal (64 chars, '.' = empty) saved with the scan
        modelId: null,
        flipGuess: false,  // orientation was proposed by recognition
    };
}

function dropScan() {
    if (S.scan && S.scan.boardUrl.startsWith('blob:')) URL.revokeObjectURL(S.scan.boardUrl);
    S.scan = null;
    S.fenView = false;
}

async function startFromFile(file) {
    if (!file || !file.type.startsWith('image/')) {
        toast(t('err.image_load'), 'error');
        return;
    }
    S.tab = 'scan';
    S.busy = true;
    render();
    try {
        const photo = await Vision.loadImage(file, PHOTO_MAX_SIDE);
        dropScan();
        S.scan = newScan(photo);
    } catch (e) {
        toast(t('err.image_load'), 'error');
    }
    S.busy = false;
    render();
    window.scrollTo({ top: 0 });
}

async function toEdit() {
    const sc = S.scan;
    let board;
    try {
        board = Vision.warp(sc.photo, Vision.orderCorners(sc.corners), BOARD_SIZE);
    } catch (e) {
        toast(t('err.invalid_corners'), 'error');
        return;
    }
    const blob = await Vision.toBlob(board);
    if (sc.boardUrl.startsWith('blob:')) URL.revokeObjectURL(sc.boardUrl);
    sc.board = board;
    sc.boardUrl = URL.createObjectURL(blob);
    if (!sc.edited && S.model) {
        S.busy = true;
        S.busyText = t('recognizing');
        render();
        try {
            await recognize(sc);
        } catch (e) {
            toast(t('recognizeFailed'), 'error');
        }
        S.busy = false;
        S.busyText = '';
    }
    sc.step = 'edit';
    sc.dirty = true;
    render();
    window.scrollTo({ top: 0 });
}

function openScan(id) {
    const s = S.scans.find(x => x.id === id);
    if (!s) return;
    const load = () => {
        dropScan();
        const cells = cellsFromPlacement(s.placement, s.flipped);
        const sc = {
            ...newScan({ width: 1, height: 1 }),
            id: s.id, step: 'edit', photo: null,
            boardUrl: `/api/scans/${s.id}/board.jpg`,
            cells, side: s.side, flipped: s.flipped, title: s.title || '',
        };
        sc.castleOff = castlingRights(boardArray(sc)).filter(c => !s.castling.includes(c));
        S.scan = sc;
        S.tab = 'scan';
        render();
        window.scrollTo({ top: 0 });
    };
    guardDiscard(load);
}

// Runs `then`, asking for confirmation first if the current scan has unsaved changes
function guardDiscard(then) {
    if (!S.scan || !S.scan.dirty) { then(); return; }
    confirmSheet(t('discardScan'), t('discardScanMsg'), t('discard'), async () => {
        closeSheet();
        then();
    });
}

function touch() {
    S.scan.dirty = true;
    render();
}

function onSquare(i) {
    const sc = S.scan;
    // Tapping a doubtful square marks it reviewed: sets the chosen piece, or confirms it if already there
    if (sc.doubt.includes(i)) {
        sc.doubt = sc.doubt.filter(x => x !== i);
        sc.cells[i] = S.brush;
    } else {
        sc.cells[i] = sc.cells[i] === S.brush ? '' : S.brush;
    }
    sc.edited = true;
    touch();
}

function openSave() {
    const sc = S.scan;
    openSheet(sc.id ? t('updateScan') : t('saveScan'), `
        <form class="stack" id="saveForm" novalidate>
            <label class="field"><span>${t('scanTitle')}</span>
                <input name="title" maxlength="120" autocomplete="off" placeholder="${esc(t('scanTitlePh'))}" value="${esc(sc.title)}"></label>
            <div class="actions">
                <button type="button" class="btn ghost" data-close>${t('cancel')}</button>
                <button type="submit" class="btn primary">${t('save')}</button>
            </div>
        </form>`, body => {
        const form = $('#saveForm', body);
        form.onsubmit = async e => {
            e.preventDefault();
            const btn = $('button[type="submit"]', form);
            btn.disabled = true;
            const pos = position(sc);
            const payload = {
                title: form.elements.title.value.trim() || null,
                placement: pos.placement, side: sc.side, castling: pos.castling, flipped: sc.flipped,
            };
            try {
                let saved;
                if (sc.id) {
                    saved = await api(`/api/scans/${sc.id}`, { method: 'PUT', body: payload });
                } else {
                    const clamp = v => Math.min(1, Math.max(0, v));
                    saved = await api('/api/scans', {
                        method: 'POST',
                        body: {
                            ...payload,
                            corners: Vision.orderCorners(sc.corners).map(([x, y]) => [clamp(x / sc.photo.width), clamp(y / sc.photo.height)]),
                            board_image: sc.board.toDataURL('image/jpeg', 0.92),
                            photo_image: sc.photo.toDataURL('image/jpeg', 0.85),
                            predicted: sc.predicted,
                            model_id: sc.predicted ? sc.modelId : null,
                        },
                    });
                    // Saved: corners can no longer change and the photo is no longer needed
                    sc.photo = null;
                    sc.board = null;
                }
                const wasNew = !sc.id;
                sc.id = saved.id;
                sc.title = saved.title || '';
                sc.dirty = false;
                closeSheet();
                toast(wasNew ? t('saved') : t('updated'));
                await reloadScans();
            } catch (err) {
                toast(errText(err), 'error');
                btn.disabled = false;
            }
        };
    });
}

function deleteScan() {
    const id = S.scan.id;
    confirmSheet(t('deleteScan'), t('deleteScanMsg'), t('delete'), async () => {
        try {
            await api(`/api/scans/${id}`, { method: 'DELETE' });
            dropScan();
            toast(t('deleted'));
            await reloadScans();
        } catch (err) {
            toast(errText(err), 'error');
        }
        closeSheet();
    });
}

/* ------------------------------------------------------ corner adjustment */

const CC = { canvas: null, ctx: null, scale: 1, dpr: 1, w: 0, h: 0, drag: -1 };

function setupCorners() {
    const canvas = $('#cornerCanvas');
    if (!canvas || !S.scan || !S.scan.photo) return;
    const photo = S.scan.photo;
    const maxW = canvas.parentElement.clientWidth;
    const maxH = Math.max(280, window.innerHeight * 0.62);
    const scale = Math.min(maxW / photo.width, maxH / photo.height);
    Object.assign(CC, {
        canvas, ctx: canvas.getContext('2d'), scale, drag: -1,
        dpr: window.devicePixelRatio || 1,
        w: Math.round(photo.width * scale), h: Math.round(photo.height * scale),
    });
    canvas.style.width = `${CC.w}px`;
    canvas.style.height = `${CC.h}px`;
    canvas.width = Math.round(CC.w * CC.dpr);
    canvas.height = Math.round(CC.h * CC.dpr);
    canvas.onpointerdown = onCornerDown;
    canvas.onpointermove = onCornerMove;
    canvas.onpointerup = canvas.onpointercancel = onCornerUp;
    drawCorners();
}

function pointerToImage(e) {
    const rect = CC.canvas.getBoundingClientRect();
    return [(e.clientX - rect.left) / CC.scale, (e.clientY - rect.top) / CC.scale];
}

function onCornerDown(e) {
    const [x, y] = pointerToImage(e);
    let best = -1;
    let bestDist = Infinity;
    S.scan.corners.forEach(([cx, cy], i) => {
        const d = Math.hypot(cx - x, cy - y) * CC.scale;
        if (d < bestDist) { best = i; bestDist = d; }
    });
    if (bestDist > 60) return;
    CC.drag = best;
    CC.canvas.setPointerCapture(e.pointerId);
    e.preventDefault();
    drawCorners();
}

function onCornerMove(e) {
    if (CC.drag < 0) return;
    const photo = S.scan.photo;
    const [x, y] = pointerToImage(e);
    S.scan.corners[CC.drag] = [Math.min(photo.width, Math.max(0, x)), Math.min(photo.height, Math.max(0, y))];
    drawCorners();
}

function onCornerUp() {
    if (CC.drag < 0) return;
    CC.drag = -1;
    drawCorners();
}

function drawCorners() {
    const { ctx, scale, dpr, w, h } = CC;
    const photo = S.scan.photo;
    const accent = cssVar('--accent');
    const pts = S.scan.corners.map(([x, y]) => [x * scale, y * scale]);
    const quad = Vision.orderCorners(pts);

    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, w, h);
    ctx.drawImage(photo, 0, 0, w, h);

    // Dim everything outside the board
    ctx.save();
    ctx.beginPath();
    ctx.rect(0, 0, w, h);
    quad.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)));
    ctx.closePath();
    ctx.globalAlpha = 0.45;
    ctx.fillStyle = cssVar('--bg');
    ctx.fill('evenodd');
    ctx.restore();

    // Projected 8x8 grid: helps check whether the corners fit
    let H = null;
    try { H = Vision.homography([[0, 0], [1, 0], [1, 1], [0, 1]], quad); } catch (e) { H = null; }
    ctx.strokeStyle = accent;
    if (H) {
        ctx.lineWidth = 1;
        ctx.globalAlpha = 0.8;
        ctx.beginPath();
        for (let i = 1; i < 8; i++) {
            const f = i / 8;
            const a = Vision.project(H, f, 0), b = Vision.project(H, f, 1);
            const c = Vision.project(H, 0, f), d = Vision.project(H, 1, f);
            ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]);
            ctx.moveTo(c[0], c[1]); ctx.lineTo(d[0], d[1]);
        }
        ctx.stroke();
        ctx.globalAlpha = 1;
    }
    ctx.lineWidth = 2;
    ctx.beginPath();
    quad.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)));
    ctx.closePath();
    ctx.stroke();

    // Handles
    pts.forEach(([x, y], i) => {
        ctx.beginPath();
        ctx.arc(x, y, i === CC.drag ? 12 : 9, 0, Math.PI * 2);
        ctx.fillStyle = accent;
        ctx.globalAlpha = i === CC.drag ? 0.35 : 0.9;
        ctx.fill();
        ctx.globalAlpha = 1;
        ctx.lineWidth = 2;
        ctx.strokeStyle = cssVar('--surface');
        ctx.stroke();
    });

    // Magnifier: the finger covers the corner, so it is shown enlarged on the opposite side
    if (CC.drag >= 0) {
        const [px, py] = pts[CC.drag];
        const R = Math.min(64, w / 5);
        const zoom = 3;
        const lx = px < w / 2 ? w - R - 8 : R + 8;
        const ly = R + 8;
        const [ix, iy] = S.scan.corners[CC.drag];
        const span = (2 * R) / (scale * zoom);
        ctx.save();
        ctx.beginPath();
        ctx.arc(lx, ly, R, 0, Math.PI * 2);
        ctx.clip();
        ctx.fillStyle = cssVar('--surface-2');
        ctx.fillRect(lx - R, ly - R, 2 * R, 2 * R);
        ctx.drawImage(photo, ix - span / 2, iy - span / 2, span, span, lx - R, ly - R, 2 * R, 2 * R);
        ctx.strokeStyle = accent;
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(lx - R, ly); ctx.lineTo(lx + R, ly);
        ctx.moveTo(lx, ly - R); ctx.lineTo(lx, ly + R);
        ctx.stroke();
        ctx.restore();
        ctx.beginPath();
        ctx.arc(lx, ly, R, 0, Math.PI * 2);
        ctx.lineWidth = 3;
        ctx.strokeStyle = accent;
        ctx.stroke();
    }
}

/* -------------------------------------------------------------- settings */

function currentTheme() {
    const v = document.documentElement.getAttribute('data-theme');
    return v === 'light' || v === 'dark' ? v : 'system';
}

function setTheme(value) {
    if (value === 'light' || value === 'dark') document.documentElement.setAttribute('data-theme', value);
    else document.documentElement.removeAttribute('data-theme');
    writeStorage('theme', value);
    // Browser status bar colour matching the theme
    const dark = value === 'dark' || (value === 'system' && matchMedia('(prefers-color-scheme: dark)').matches);
    $$('meta[name="theme-color"]').forEach(m => m.setAttribute('content', dark ? THEME_COLORS.dark : THEME_COLORS.light));
}

function openSettings() {
    const theme = currentTheme();
    openSheet(t('settings'), `
        <section class="set">
            <h3>${t('theme')}</h3>
            <div class="chips">${['system', 'light', 'dark'].map(v =>
                `<button type="button" class="chip${v === theme ? ' on' : ''}" data-theme-opt="${v}">${t(`themeOpt.${v}`)}</button>`).join('')}</div>
            <p class="hint">${t('themeHint')}</p>
        </section>
        <section class="set">
            <h3>${t('language')}</h3>
            <div class="chips">${Object.keys(I18N).map(l =>
                `<button type="button" class="chip${l === S.lang ? ' on' : ''}" data-lang-opt="${l}">${l.toUpperCase()}</button>`).join('')}</div>
        </section>
        ${renderModelSettings()}
        <p class="hint">${esc(t('version', { v: S.version || '–' }))}</p>`);
}

function renderModelSettings() {
    const m = S.model;
    const acc = m && m.metrics && m.metrics.real_val_acc != null
        ? `<p class="hint">${esc(t('modelAcc', { acc: `${(m.metrics.real_val_acc * 100).toFixed(1)} %` }))}</p>` : '';
    const info = m
        ? `<div class="set-row"><span>${esc(t('modelInfo', { id: m.id, date: fmtDate(m.created) }))}</span>
               <span class="tag${m.source === 'uploaded' ? ' ok' : ''}">${t(m.source === 'uploaded' ? 'modelUploaded' : 'modelBundled')}</span></div>${acc}`
        : `<p class="hint">${t('modelNone')}</p>`;
    return `
        <section class="set">
            <h3>${t('model')}</h3>
            ${info}
            <div class="actions">
                ${m && m.source === 'uploaded' ? `<button type="button" class="btn small ghost" data-action="reset-model">${t('resetModel')}</button>` : ''}
                <label class="btn small ghost">${t('uploadModel')}
                    <input type="file" accept=".json,.bin" multiple data-model-file hidden></label>
            </div>
            <p class="hint">${t('uploadModelHint')}</p>
        </section>`;
}

async function uploadModel(files) {
    const pick = ext => files.find(f => f.name.toLowerCase().endsWith(ext));
    const meta = pick('.json');
    const weights = pick('.bin');
    if (files.length !== 2 || !meta || !weights) {
        toast(t('err.model_files'), 'error');
        return;
    }
    const form = new FormData();
    form.append('meta', meta);
    form.append('weights', weights);
    try {
        let res;
        try {
            res = await fetch('/api/model', { method: 'POST', body: form });
        } catch (e) {
            throw new Error('network');
        }
        const data = await res.json().catch(() => ({}));
        if (!res.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'generic');
        S.model = data;
        loadNet().catch(() => {});
        toast(t('modelSaved'));
        openSettings();
    } catch (err) {
        toast(errText(err), 'error');
    }
}

async function resetModel() {
    try {
        S.model = await api('/api/model', { method: 'DELETE' });
        loadNet().catch(() => {});
        toast(t('modelResetDone'));
    } catch (err) {
        if (err.message === 'model_missing') S.model = null;
        toast(errText(err), 'error');
    }
    openSettings();
}

/* ---------------------------------------------------------------- events */

async function onAction(action, el) {
    const sc = S.scan;
    if (action === 'goto-scan') {
        S.tab = 'scan';
        render();
        window.scrollTo({ top: 0 });
        return;
    }
    if (action === 'rotate') {
        sc.photo = Vision.rotate90(sc.photo);
        const fresh = newScan(sc.photo);
        sc.corners = fresh.corners;
        render();
        return;
    }
    if (action === 'discard' || action === 'new-scan') {
        guardDiscard(() => { dropScan(); render(); window.scrollTo({ top: 0 }); });
        return;
    }
    if (action === 'to-edit') return toEdit();
    if (action === 'adjust-corners') {
        sc.step = 'corners';
        render();
        window.scrollTo({ top: 0 });
        return;
    }
    if (action === 'clear-board') {
        confirmSheet(t('clearBoard'), t('clearBoardMsg'), t('clearBoard'), async () => {
            closeSheet();
            sc.cells = Array(64).fill('');
            sc.doubt = [];
            sc.edited = true;
            touch();
        });
        return;
    }
    if (action === 'copy-fen') {
        const ok = await copyText(position(sc).fen);
        if (ok) toast(t('copied'));
        else {
            toast(t('copyFailed'), 'error');
            $('#fenField').select();
        }
        return;
    }
    if (action === 'save-scan') return openSave();
    if (action === 'delete-scan') return deleteScan();
    if (action === 'reset-model') {
        el.disabled = true;
        return resetModel();
    }
}

document.addEventListener('click', e => {
    if (e.target.closest('[data-close]')) { closeSheet(); return; }
    const sq = e.target.closest('[data-sq]');
    if (sq) { onSquare(Number(sq.dataset.sq)); return; }
    const brush = e.target.closest('[data-brush]');
    if (brush) { S.brush = brush.dataset.brush; render(); return; }
    const action = e.target.closest('[data-action]');
    if (action) { onAction(action.dataset.action, action); return; }
    const scan = e.target.closest('[data-scan]');
    if (scan) { openScan(Number(scan.dataset.scan)); return; }
    // Photo / Diagram / FEN: the FEN view replaces the board and is not remembered across scans
    const view = e.target.closest('[data-view]');
    if (view) {
        S.fenView = view.dataset.view === 'fen';
        if (!S.fenView) { S.boardView = view.dataset.view; writeStorage('boardView', S.boardView); }
        render();
        return;
    }
    const side = e.target.closest('[data-side]');
    if (side) { S.scan.side = side.dataset.side; touch(); return; }
    const flip = e.target.closest('[data-flip]');
    if (flip) { S.scan.flipped = flip.dataset.flip === '1'; S.scan.flipGuess = false; touch(); return; }
    const castle = e.target.closest('[data-castle]');
    if (castle) {
        const c = castle.dataset.castle;
        const off = S.scan.castleOff;
        S.scan.castleOff = off.includes(c) ? off.filter(x => x !== c) : [...off, c];
        touch();
        return;
    }
    const themeOpt = e.target.closest('[data-theme-opt]');
    if (themeOpt) {
        setTheme(themeOpt.dataset.themeOpt);
        $$('.chip', themeOpt.parentElement).forEach(c => c.classList.toggle('on', c === themeOpt));
        return;
    }
    const langOpt = e.target.closest('[data-lang-opt]');
    if (langOpt) { setLang(langOpt.dataset.langOpt); openSettings(); }
});

document.addEventListener('change', e => {
    if (e.target.matches('input[data-file]')) startFromFile(e.target.files[0]);
    else if (e.target.matches('input[data-model-file]')) uploadModel(Array.from(e.target.files));
});

// Paste a screenshot (desktop)
document.addEventListener('paste', e => {
    const item = Array.from((e.clipboardData && e.clipboardData.items) || []).find(i => i.type.startsWith('image/'));
    if (!item || !$('#sheet').hidden) return;
    e.preventDefault();
    const file = item.getAsFile();
    guardDiscard(() => startFromFile(file));
});

document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && !$('#sheet').hidden) closeSheet();
});

let resizeFrame = 0;
window.addEventListener('resize', () => {
    cancelAnimationFrame(resizeFrame);
    resizeFrame = requestAnimationFrame(() => {
        if (S.tab === 'scan' && S.scan && S.scan.step === 'corners') setupCorners();
    });
});

$('#settingsBtn').onclick = openSettings;
$$('#tabs .tab').forEach(b => {
    b.onclick = () => {
        if (S.tab === b.dataset.tab) { window.scrollTo({ top: 0, behavior: 'smooth' }); return; }
        S.tab = b.dataset.tab;
        render();
        window.scrollTo({ top: 0 });
    };
});

// Top bar: solid with the small title as soon as the large title scrolls out of view
function updateTopbar() {
    $('#topbar').classList.toggle('scrolled', window.scrollY > 36);
}
window.addEventListener('scroll', updateTopbar, { passive: true });
updateTopbar();

// Sheet: drag down from the header to close (mobile only)
(function sheetDrag() {
    const panel = $('.sheet-panel');
    const head = $('#sheetHead');
    let startY = null;
    let dy = 0;
    head.addEventListener('pointerdown', e => {
        if (e.target.closest('button') || window.matchMedia('(min-width: 720px)').matches) return;
        startY = e.clientY;
        dy = 0;
        panel.classList.add('dragging');
        panel.classList.remove('settle');
        head.setPointerCapture(e.pointerId);
    });
    head.addEventListener('pointermove', e => {
        if (startY == null) return;
        dy = Math.max(0, e.clientY - startY);
        panel.style.transform = `translateY(${dy}px)`;
    });
    const end = () => {
        if (startY == null) return;
        startY = null;
        panel.classList.remove('dragging');
        if (dy > 110) {
            closeSheet();
        } else {
            panel.classList.add('settle');
            panel.style.transform = '';
        }
    };
    head.addEventListener('pointerup', end);
    head.addEventListener('pointercancel', end);
})();

setLang(S.lang, false);
loadAll();
