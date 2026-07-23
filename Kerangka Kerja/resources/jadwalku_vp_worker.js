/**
 * JadwalKu Voice Pack Store - Cloudflare Worker
 * Menggunakan @huggingface/hub untuk manajemen dataset.
 */

import { commit, listFiles } from "@huggingface/hub";

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

        // Cek database KV (Hanya 1 paket per Hardware ID)
        const existingDataStr = await env.VP_STORE_DB.get(hwId);
        let oldFilename = null;
        if (existingDataStr) {
            const existingData = JSON.parse(existingDataStr);
            // Cek password untuk mencegah penimpaan oleh orang lain
            if (existingData.password !== passwordHash) {
                return jsonResponse({error: 'Password salah untuk paket yang sudah ada!'}, 403);
            }
            oldFilename = existingData.filename;
        }

        // Convert base64 to Blob
        const binaryString = atob(b64content);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }
        const contentBlob = new Blob([bytes]);

        // Siapkan operasi Commit Hugging Face (Format @huggingface/hub)
        const ops = [];
        if (oldFilename && oldFilename !== finalFilename) {
            ops.push({ operation: 'delete', path: oldFilename });
        }
        ops.push({
            operation: 'addOrUpdate',
            path: finalFilename,
            content: contentBlob
        });

        try {
            await commit({
                repo: { type: "dataset", name: HF_REPO },
                credentials: { accessToken: env.HF_TOKEN },
                title: `Upload VP by ${uploaderName}`,
                operations: ops
            });
        } catch (e) {
            return new Response(JSON.stringify({ error: `HF API Error: ${e.message}` }), {
                status: 500, headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
            });
        }

        // Simpan metadata baru ke KV
        const newMeta = {
            id: hwId,
            password: passwordHash,
            filename: finalFilename,
            pack_name: packName,
            uploader_name: uploaderName,
            updated_at: new Date().toISOString()
        };
        await env.VP_STORE_DB.put(hwId, JSON.stringify(newMeta));

        return jsonResponse({success: true, message: 'Paket Suara berhasil diunggah!'});

    } catch (e) {
        return jsonResponse({error: e.message}, 500);
    }
}

async function handleList(request, env) {
    try {
        const hfListResp = await fetch(`https://huggingface.co/api/datasets/OrionWood/JadwalKu-VoicePacks/tree/main`, {
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
                    url: `https://huggingface.co/datasets/OrionWood/JadwalKu-VoicePacks/resolve/main/${f.path}`,
                    size: f.size,
                    pack_name: meta.pack_name,
                    uploader_name: meta.uploader_name,
                    updated_at: meta.updated_at
                });
            } else {
                // Fallback jika KV kosong atau nama tidak cocok
                const parts = f.path.replace('.jvp', '').split('_');
                const hwIdPart = parts[0];
                const packNamePart = parts.slice(1).join(' ');
                result.push({
                    filename: f.path,
                    url: `https://huggingface.co/datasets/OrionWood/JadwalKu-VoicePacks/resolve/main/${f.path}`,
                    size: f.size,
                    pack_name: packNamePart || 'Unknown Pack',
                    uploader_name: 'Unknown',
                    updated_at: new Date().toISOString()
                });
            }
        }

        return jsonResponse({success: true, data: result});

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
