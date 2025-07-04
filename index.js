const {
    default: makeWASocket,
    DisconnectReason,
    useMultiFileAuthState,
    fetchLatestBaileysVersion,
    jidNormalizedUser,
    PHONENUMBER_MCC,
} = require("baileys");

const { Boom } = require("@hapi/boom");
const pino = require("pino");
const { exec } = require("child_process");
const fs = require("fs");
const qrcode = require("qrcode-terminal"); // <-- ADD THIS LINE

const logger = pino().child({ level: "silent" });

const runPythonScript = (text, sender, sock) => {
    exec(`python ai.py "${text}" "${sender}"`, (error, stdout, stderr) => {
        if (error) {
            console.error("❌ Python Error:", error.message);
            return;
        }

        const reply = stdout.trim();
        if (reply) {
            sock.sendMessage(sender, { text: reply });
            console.log(`📤 To ${sender}: ${reply}`);
        } else {
            console.log("⚠️ No reply returned.");
        }
    });
};

async function startSock() {
    const { state, saveCreds } = await useMultiFileAuthState(
        "./baileys_auth_info",
    ); // Ensure this path is correct
    const { version, isLatest } = await fetchLatestBaileysVersion();
    console.log(
        `Using baileys version ${version}${isLatest ? "" : " (outdated)"}`,
    );

    const sock = makeWASocket({
        version,
        logger: pino({ level: "silent" }),
        // printQRInTerminal: true, // <-- REMOVE OR COMMENT OUT THIS LINE
        auth: state,
        browser: ["Ubuntu", "Chrome", "110.0.0.0"],
    });

    sock.ev.on("creds.update", saveCreds);

    sock.ev.on("connection.update", (update) => {
        const { connection, lastDisconnect, qr } = update; // <-- ADD 'qr' here
        if (connection === "close") {
            let reason = new Boom(lastDisconnect?.error)?.output?.statusCode;
            if (
                reason === DisconnectReason.badSession ||
                reason === DisconnectReason.loggedOut
            ) {
                console.log("Logged out. Please scan the QR code again.");
                // fs.rmSync('./baileys_auth_info', { recursive: true, force: true }); // Uncomment if you want to delete auth on logout
                startSock();
            } else {
                console.log("Connection closed. Reconnecting...");
                startSock();
            }
        } else if (qr) {
            // <-- ADD THIS BLOCK TO HANDLE QR
            qrcode.generate(qr, { small: true });
            console.log("Scan the QR code above to connect your WhatsApp bot.");
        } else if (connection === "open") {
            console.log("✅ WhatsApp bot is ready and running!");
        }
    });

    sock.ev.on("messages.upsert", async ({ messages, type }) => {
        const msg = messages[0];
        if (!msg.message || msg.key.fromMe) return;

        const sender = msg.key.remoteJid;
        const text =
            msg.message.conversation ||
            msg.message.extendedTextMessage?.text ||
            msg.message.imageMessage?.caption ||
            msg.message.videoMessage?.caption;

        if (!text) return;

        console.log(`📥 From ${sender}: ${text}`);
        runPythonScript(text, sender, sock);
    });
}

startSock();
