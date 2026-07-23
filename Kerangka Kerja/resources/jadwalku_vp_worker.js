/**
 * JadwalKu Voice Pack Store - Cloudflare Worker
 * Menggunakan manual LFS Protocol untuk menghindari 1102 CPU Time Limit.
 */

import { Buffer } from "node:buffer";

const HF_REPO = "OrionWood/JadwalKu-VoicePacks";

export default {
    async fetch(request, env, ctx) {
        if (request.method === 'OPTIONS') {
            return new Response(null, {
                headers: {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': '*'
                }
            });
        }

        const url = new URL(request.url);
        
        if (url.pathname === '/upload' && request.method === 'POST') {
            return await handleUpload(request, env);
        } else if (url.pathname === '/list' && request.method === 'GET') {
            return await handleList(request, env);
        } else if (url.pathname.startsWith('/download/') && request.method === 'GET') {
            return await handleDownload(request, env, url.pathname);
        }

        return new Response('JadwalKu Voice Pack API Running.', { status: 200 });
    }
};

async function handleUpload(request, env) {
    try {
        const hwId = request.headers.get('X-Hardware-ID');
        const passwordHash = request.headers.get('X-Password');
        
        if (!hwId || !passwordHash) {
            return jsonResponse({error: 'Parameter tidak lengkap.'}, 400);
        }

        // Parse JSON payload dari klien
        const reqJson = await request.json();
        let uploaderName = (reqJson.uploader_name || 'Unknown').substring(0, 50).replace(/[^a-zA-Z0-9 _-]/g, '').trim();
        let packName = (reqJson.pack_name || 'VoicePack').substring(0, 50).replace(/[^a-zA-Z0-9 _-]/g, '').trim();
        const b64content = reqJson.b64content;

        if (!b64content) {
            return jsonResponse({error: 'Konten file kosong.'}, 400);
        }
        
        const shortId = hwId.substring(0, 8);
        const safePackName = packName.replace(/ /g, '_');
        const finalFilename = `${shortId}_${safePackName}.jvp`;

        // Cek database KV
        const existingDataStr = await env.VP_STORE_DB.get(hwId);
        let oldFilename = null;
        if (existingDataStr) {
            const existingData = JSON.parse(existingDataStr);
            if (existingData.password !== passwordHash) {
                return jsonResponse({error: 'Password salah untuk paket yang sudah ada!'}, 403);
            }
            oldFilename = existingData.filename;
        }

        // Convert base64 to Buffer
        const buffer = Buffer.from(b64content, 'base64');
        const size = buffer.length;

        // Hash (WebCrypto API)
        const hashBuffer = await crypto.subtle.digest('SHA-256', buffer);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        const sha256Hex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');

        // 1. Get LFS Presigned URL
        const lfsBatchUrl = `https://huggingface.co/datasets/${HF_REPO}.git/info/lfs/objects/batch`;
        const lfsPayload = {
            operation: "upload",
            transfers: ["basic"],
            objects: [{ oid: sha256Hex, size: size }]
        };
        const lfsResp = await fetch(lfsBatchUrl, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${env.HF_TOKEN}`,
                'Accept': 'application/vnd.git-lfs+json',
                'Content-Type': 'application/vnd.git-lfs+json'
            },
            body: JSON.stringify(lfsPayload)
        });

        if (!lfsResp.ok) {
            const err = await lfsResp.text();
            return jsonResponse({error: `HF LFS Batch Error: ${err}`}, 500);
        }

        const lfsData = await lfsResp.json();
        const uploadAction = lfsData.objects?.[0]?.actions?.upload;
        
        // 2. Upload to S3 if needed
        if (uploadAction) {
            const uploadUrl = uploadAction.href;
            const uploadHeaders = uploadAction.header || {};
            
            const s3Resp = await fetch(uploadUrl, {
                method: 'PUT',
                headers: uploadHeaders,
                body: buffer
            });
            
            if (!s3Resp.ok) {
                const s3Err = await s3Resp.text();
                return jsonResponse({error: `S3 Upload Error: ${s3Err}`}, 500);
            }
        }

        // 3. Commit LFS Pointer
        const pointerContent = `version https://git-lfs.github.com/spec/v1\noid sha256:${sha256Hex}\nsize ${size}\n`;
        const b64Pointer = Buffer.from(pointerContent).toString('base64');

        const commitOps = [];
        commitOps.push(JSON.stringify({
            key: "header",
            value: { summary: `Upload VP by ${uploaderName}` }
        }));
        if (oldFilename && oldFilename !== finalFilename) {
            commitOps.push(JSON.stringify({
                key: "deletedFile",
                value: { path: oldFilename }
            }));
        }
        commitOps.push(JSON.stringify({
            key: "file",
            value: {
                content: b64Pointer,
                path: finalFilename,
                encoding: "base64"
            }
        }));

        const ndjsonBody = commitOps.join('\n');
        const commitUrl = `https://huggingface.co/api/datasets/${HF_REPO}/commit/main`;
        const commitResp = await fetch(commitUrl, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${env.HF_TOKEN}`,
                'Content-Type': 'application/x-ndjson'
            },
            body: ndjsonBody
        });

        if (!commitResp.ok) {
            const commitErr = await commitResp.text();
            return jsonResponse({error: `HF Commit Error: ${commitErr}`}, 500);
        }

        // 4. Update KV Metadata
        const newMeta = {
            hardwareId: hwId,
            password: passwordHash,
            filename: finalFilename,
            pack_name: packName,
            uploader: uploaderName,
            uploadDate: new Date().toISOString(),
            downloadCount: 0
        };
        await env.VP_STORE_DB.put(hwId, JSON.stringify(newMeta));

        return jsonResponse({success: true, message: 'Paket Suara berhasil diunggah!'});

    } catch (e) {
        return jsonResponse({error: e.message}, 500);
    }
}

async function handleList(request, env) {
    try {
        const hfListResp = await fetch(`https://huggingface.co/api/datasets/${HF_REPO}/tree/main`, {
            headers: { 'Authorization': `Bearer ${env.HF_TOKEN}` }
        });
        
        if (!hfListResp.ok) throw new Error('Gagal mengambil daftar dari HF');
        
        const files = await hfListResp.json();
        const jvpFiles = files.filter(f => f.path.endsWith('.jvp'));

        // Baca metadata dari KV
        const listData = await env.VP_STORE_DB.list();
        const packDict = {};
        for (const key of listData.keys) {
            const valStr = await env.VP_STORE_DB.get(key.name);
            if (valStr) {
                const val = JSON.parse(valStr);
                packDict[val.filename] = val;
            }
        }

        const result = [];
        for (const f of jvpFiles) {
            const meta = packDict[f.path];
            if (meta) {
                result.push({
                    filename: f.path,
                    url: `https://huggingface.co/datasets/${HF_REPO}/resolve/main/${f.path}`,
                    size: f.size,
                    pack_name: meta.pack_name || meta.filename,
                    uploader: meta.uploader || meta.uploader_name || 'Unknown',
                    uploadDate: meta.uploadDate || meta.updated_at || new Date().toISOString(),
                    hardwareId: meta.hardwareId || meta.id || 'Unknown',
                    downloadCount: meta.downloadCount || 0
                });
            } else {
                // Fallback jika KV kosong atau nama tidak cocok
                const parts = f.path.replace('.jvp', '').split('_');
                const hwIdPart = parts[0];
                const packNamePart = parts.slice(1).join(' ');
                result.push({
                    filename: f.path,
                    url: `https://huggingface.co/datasets/${HF_REPO}/resolve/main/${f.path}`,
                    size: f.size,
                    pack_name: packNamePart || 'Unknown Pack',
                    uploader: 'Anonim',
                    uploadDate: new Date().toISOString(),
                    hardwareId: hwIdPart,
                    downloadCount: 0
                });
            }
        }

        return jsonResponse({success: true, data: result});

    } catch (e) {
        return jsonResponse({error: e.message}, 500);
    }
}

async function handleDownload(request, env, pathname) {
    try {
        const hwId = decodeURIComponent(pathname.replace('/download/', ''));
        if (!hwId) return jsonResponse({error: 'Hardware ID kosong'}, 400);

        const dataStr = await env.VP_STORE_DB.get(hwId);
        if (!dataStr) return jsonResponse({error: 'Paket tidak ditemukan'}, 404);

        const meta = JSON.parse(dataStr);
        const fileUrl = `https://huggingface.co/datasets/${HF_REPO}/resolve/main/${meta.filename}`;
        
        // Update download count (fire and forget)
        meta.downloadCount = (meta.downloadCount || 0) + 1;
        env.VP_STORE_DB.put(hwId, JSON.stringify(meta)).catch(e => console.error(e));

        return Response.redirect(fileUrl, 302);
    } catch (e) {
        return jsonResponse({error: e.message}, 500);
    }
}

function jsonResponse(data, status = 200) {
    return new Response(JSON.stringify(data), {
        status: status,
        headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    });
}
