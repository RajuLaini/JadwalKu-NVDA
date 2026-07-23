import { commit } from "@huggingface/hub";

const HF_TOKEN = "xxx";

async function main() {
    try {
        const result = await commit({
            repo: { type: "dataset", name: "OrionWood/JadwalKu-VoicePacks" },
            credentials: { accessToken: HF_TOKEN },
            title: "Test upload using JS hub library",
            operations: [
                {
                    operation: "addOrUpdate",
                    path: "testfile_lib.jvp",
                    content: new Blob([new Uint8Array([80, 75, 3, 4, 0, 0, 0, 0])])
                }
            ]
        });
        console.log("Success!", result);
    } catch (e) {
        console.error("Error:", e);
    }
}

main();
