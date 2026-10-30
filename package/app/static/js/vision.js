'use strict';

/* In-browser computer vision (no libraries): image loading,
   homographies and board rectification. Exposes the global `Vision` object. */

const Vision = (() => {
    /* ------------------------------------------------------------ images */

    // Opens an image File/Blob honouring EXIF orientation and downscales it to maxSide px
    async function loadImage(file, maxSide) {
        const url = URL.createObjectURL(file);
        try {
            const img = new Image();
            img.src = url;
            await img.decode();
            const k = Math.min(1, maxSide / Math.max(img.naturalWidth, img.naturalHeight));
            const canvas = document.createElement('canvas');
            canvas.width = Math.max(1, Math.round(img.naturalWidth * k));
            canvas.height = Math.max(1, Math.round(img.naturalHeight * k));
            const ctx = canvas.getContext('2d');
            ctx.imageSmoothingQuality = 'high';
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            return canvas;
        } finally {
            URL.revokeObjectURL(url);
        }
    }

    // Rotates a canvas 90° clockwise
    function rotate90(src) {
        const out = document.createElement('canvas');
        out.width = src.height;
        out.height = src.width;
        const ctx = out.getContext('2d');
        ctx.translate(out.width, 0);
        ctx.rotate(Math.PI / 2);
        ctx.drawImage(src, 0, 0);
        return out;
    }

    function toBlob(canvas, type = 'image/jpeg', quality = 0.92) {
        return new Promise(resolve => canvas.toBlob(resolve, type, quality));
    }

    /* ---------------------------------------------------------- geometry */

    // Orders 4 points as [top-left, top-right, bottom-right, bottom-left]
    function orderCorners(pts) {
        const cx = pts.reduce((s, p) => s + p[0], 0) / 4;
        const cy = pts.reduce((s, p) => s + p[1], 0) / 4;
        const ring = pts.slice().sort((a, b) => Math.atan2(a[1] - cy, a[0] - cx) - Math.atan2(b[1] - cy, b[0] - cx));
        // with the y axis pointing down atan2 goes clockwise; start at the smallest x+y
        let first = 0;
        ring.forEach((p, i) => { if (p[0] + p[1] < ring[first][0] + ring[first][1]) first = i; });
        return ring.slice(first).concat(ring.slice(0, first)).map(p => [p[0], p[1]]);
    }

    // 3x3 homography (array of 9, h8 = 1) mapping the 4 src points to the 4 dst points
    function homography(src, dst) {
        const A = [];
        for (let i = 0; i < 4; i++) {
            const [x, y] = src[i];
            const [X, Y] = dst[i];
            A.push([x, y, 1, 0, 0, 0, -x * X, -y * X, X]);
            A.push([0, 0, 0, x, y, 1, -x * Y, -y * Y, Y]);
        }
        // Gaussian elimination with partial pivoting on the 8x9 augmented matrix
        for (let col = 0; col < 8; col++) {
            let pivot = col;
            for (let r = col + 1; r < 8; r++) if (Math.abs(A[r][col]) > Math.abs(A[pivot][col])) pivot = r;
            if (Math.abs(A[pivot][col]) < 1e-12) throw new Error('degenerate');
            [A[col], A[pivot]] = [A[pivot], A[col]];
            for (let r = 0; r < 8; r++) {
                if (r === col) continue;
                const f = A[r][col] / A[col][col];
                if (f === 0) continue;
                for (let c = col; c < 9; c++) A[r][c] -= f * A[col][c];
            }
        }
        const h = A.map((row, i) => row[8] / row[i]);
        h.push(1);
        return h;
    }

    function project(H, x, y) {
        const w = H[6] * x + H[7] * y + H[8];
        return [(H[0] * x + H[1] * y + H[2]) / w, (H[3] * x + H[4] * y + H[5]) / w];
    }

    /* ------------------------------------------------------ rectification */

    // Projects the quadrilateral `quad` (ordered, in `src` px) onto a square size x size canvas.
    // 2x2 supersampling with bilinear interpolation to keep detail when downscaling.
    function warp(src, quad, size) {
        const H = homography([[0, 0], [size, 0], [size, size], [0, size]], quad);
        const sw = src.width;
        const sh = src.height;
        const s = src.getContext('2d').getImageData(0, 0, sw, sh).data;
        const out = document.createElement('canvas');
        out.width = out.height = size;
        const octx = out.getContext('2d');
        const img = octx.createImageData(size, size);
        const d = img.data;
        const offsets = [0.25, 0.75];
        for (let y = 0; y < size; y++) {
            for (let x = 0; x < size; x++) {
                let r = 0, g = 0, b = 0;
                for (const oy of offsets) {
                    for (const ox of offsets) {
                        const px = x + ox, py = y + oy;
                        const w = H[6] * px + H[7] * py + H[8];
                        // Pixel indices: the centre of pixel i is at i + 0.5
                        let u = (H[0] * px + H[1] * py + H[2]) / w - 0.5;
                        let v = (H[3] * px + H[4] * py + H[5]) / w - 0.5;
                        u = u < 0 ? 0 : (u > sw - 1 ? sw - 1 : u);
                        v = v < 0 ? 0 : (v > sh - 1 ? sh - 1 : v);
                        const x0 = Math.floor(u), y0 = Math.floor(v);
                        const x1 = x0 + 1 < sw ? x0 + 1 : x0, y1 = y0 + 1 < sh ? y0 + 1 : y0;
                        const fx = u - x0, fy = v - y0;
                        const i00 = (y0 * sw + x0) * 4, i10 = (y0 * sw + x1) * 4;
                        const i01 = (y1 * sw + x0) * 4, i11 = (y1 * sw + x1) * 4;
                        const w00 = (1 - fx) * (1 - fy), w10 = fx * (1 - fy), w01 = (1 - fx) * fy, w11 = fx * fy;
                        r += s[i00] * w00 + s[i10] * w10 + s[i01] * w01 + s[i11] * w11;
                        g += s[i00 + 1] * w00 + s[i10 + 1] * w10 + s[i01 + 1] * w01 + s[i11 + 1] * w11;
                        b += s[i00 + 2] * w00 + s[i10 + 2] * w10 + s[i01 + 2] * w01 + s[i11 + 2] * w11;
                    }
                }
                const o = (y * size + x) * 4;
                d[o] = r / 4;
                d[o + 1] = g / 4;
                d[o + 2] = b / 4;
                d[o + 3] = 255;
            }
        }
        octx.putImageData(img, 0, 0);
        return out;
    }

    /* ---------------------------------------------------- recognition (CNN) */

    // Contract with training/common.py (preprocess_version 1): 512x512 board -> grey -> 2x2 mean ->
    // levels by 1 % / 99 % percentiles -> 8-bit quantised -> 64 tiles of 32x32 in visual order.
    const TILE = 32;
    const TILE_PIXELS = TILE * TILE;

    function boardInput(board) {
        const n = board.width;
        if (n !== 512 || board.height !== 512) throw new Error('board_size');
        const d = board.getContext('2d').getImageData(0, 0, n, n).data;
        const half = n / 2;
        const g = new Float32Array(half * half);
        const hist = new Uint32Array(256);
        for (let y = 0; y < half; y++) {
            for (let x = 0; x < half; x++) {
                let sum = 0;
                for (let dy = 0; dy < 2; dy++) {
                    for (let dx = 0; dx < 2; dx++) {
                        const o = ((2 * y + dy) * n + 2 * x + dx) * 4;
                        sum += 0.299 * d[o] + 0.587 * d[o + 1] + 0.114 * d[o + 2];
                    }
                }
                const v = sum / 4;
                g[y * half + x] = v;
                hist[Math.min(255, Math.max(0, Math.floor(v)))]++;
            }
        }
        const total = half * half;
        const level = frac => {
            let cum = 0;
            for (let i = 0; i < 256; i++) {
                cum += hist[i];
                if (cum >= frac * total) return i;
            }
            return 255;
        };
        const lo = level(0.01);
        const span = Math.max(level(0.99) - lo, 16);
        const out = new Float32Array(64 * TILE_PIXELS);
        for (let sq = 0; sq < 64; sq++) {
            const r0 = (sq >> 3) * TILE;
            const c0 = (sq & 7) * TILE;
            for (let y = 0; y < TILE; y++) {
                for (let x = 0; x < TILE; x++) {
                    const v = Math.min(1, Math.max(0, (g[(r0 + y) * half + c0 + x] - lo) / span));
                    out[sq * TILE_PIXELS + y * TILE + x] = Math.round(v * 255) / 255;
                }
            }
        }
        return out;
    }

    // meta: model.json from /api/model; buffer: ArrayBuffer of the weights (float32 little-endian)
    function createNet(meta, buffer) {
        if (buffer.byteLength !== meta.weights_count * 4) throw new Error('invalid_model');
        const all = new Float32Array(buffer);
        const take = ref => all.subarray(ref[0], ref[0] + ref[1]);
        const layers = meta.layers.map(l => ({ ...l, w: l.weight ? take(l.weight) : null, b: l.bias ? take(l.bias) : null }));
        return { id: meta.id, classes: meta.classes, layers };
    }

    // 3x3 convolution with padding 1 (the only one train.py exports): the zero border is added once
    // and the 9 weights live in local variables; this loop dominates recognition time.
    function conv2d(src, c, h, w, l) {
        if (l.kernel !== 3 || l.pad !== 1) throw new Error('invalid_model');
        const pw = w + 2, ph = h + 2, plane = pw * ph;
        const pad = new Float32Array(c * plane);
        for (let ci = 0; ci < c; ci++) {
            for (let y = 0; y < h; y++) pad.set(src.subarray((ci * h + y) * w, (ci * h + y + 1) * w), ci * plane + (y + 1) * pw + 1);
        }
        const oc = l.out, W = l.w, n = h * w;
        const out = new Float32Array(oc * n);
        for (let o = 0; o < oc; o++) {
            const ob = o * n;
            out.fill(l.b[o], ob, ob + n);
            for (let ci = 0; ci < c; ci++) {
                const k = (o * c + ci) * 9;
                const w0 = W[k], w1 = W[k + 1], w2 = W[k + 2], w3 = W[k + 3], w4 = W[k + 4];
                const w5 = W[k + 5], w6 = W[k + 6], w7 = W[k + 7], w8 = W[k + 8];
                const ib = ci * plane;
                for (let y = 0; y < h; y++) {
                    const r0 = ib + y * pw, r1 = r0 + pw, r2 = r1 + pw, orow = ob + y * w;
                    for (let x = 0; x < w; x++) {
                        out[orow + x] += w0 * pad[r0 + x] + w1 * pad[r0 + x + 1] + w2 * pad[r0 + x + 2]
                            + w3 * pad[r1 + x] + w4 * pad[r1 + x + 1] + w5 * pad[r1 + x + 2]
                            + w6 * pad[r2 + x] + w7 * pad[r2 + x + 1] + w8 * pad[r2 + x + 2];
                    }
                }
            }
        }
        if (l.relu) for (let i = 0; i < out.length; i++) if (out[i] < 0) out[i] = 0;
        return out;
    }

    function maxpool(src, c, h, w, s) {
        const oh = Math.floor(h / s), ow = Math.floor(w / s);
        const out = new Float32Array(c * oh * ow);
        for (let ci = 0; ci < c; ci++) {
            for (let y = 0; y < oh; y++) {
                for (let x = 0; x < ow; x++) {
                    let m = -Infinity;
                    for (let dy = 0; dy < s; dy++) {
                        for (let dx = 0; dx < s; dx++) {
                            const v = src[(ci * h + y * s + dy) * w + x * s + dx];
                            if (v > m) m = v;
                        }
                    }
                    out[(ci * oh + y) * ow + x] = m;
                }
            }
        }
        return out;
    }

    function dense(src, l) {
        const out = new Float32Array(l.out);
        for (let o = 0; o < l.out; o++) {
            let s = l.b[o];
            const row = o * l.in;
            for (let i = 0; i < l.in; i++) s += l.w[row + i] * src[i];
            out[o] = l.relu && s < 0 ? 0 : s;
        }
        return out;
    }

    // Logits for one square (32x32 Float32Array in [0, 1])
    function forward(net, tile) {
        let a = tile, c = 1, h = TILE, w = TILE;
        for (const l of net.layers) {
            if (l.type === 'conv2d') { a = conv2d(a, c, h, w, l); c = l.out; }
            else if (l.type === 'maxpool2d') { a = maxpool(a, c, h, w, l.size); h = Math.floor(h / l.size); w = Math.floor(w / l.size); }
            else if (l.type === 'dense') a = dense(a, l);
            else if (l.type !== 'flatten') throw new Error('invalid_model');
        }
        return a;
    }

    function softmax(z) {
        const m = Math.max(...z);
        const e = Array.from(z, v => Math.exp(v - m));
        const s = e.reduce((x, y) => x + y, 0);
        return e.map(v => v / s);
    }

    // 64 squares -> [{ piece, conf }] in visual order. Yields every row so the UI doesn't freeze.
    async function classify(net, input) {
        const out = [];
        for (let sq = 0; sq < 64; sq++) {
            const p = softmax(forward(net, input.subarray(sq * TILE_PIXELS, (sq + 1) * TILE_PIXELS)));
            let best = 0;
            for (let i = 1; i < p.length; i++) if (p[i] > p[best]) best = i;
            out.push({ piece: net.classes[best], conf: p[best] });
            if ((sq & 7) === 7) await new Promise(r => setTimeout(r, 0));
        }
        return out;
    }

    return { loadImage, rotate90, toBlob, orderCorners, homography, project, warp, boardInput, createNet, forward, classify };
})();
