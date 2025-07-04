const { Client, LocalAuth } = require("whatsapp-web.js");
const qrcode = require("qrcode-terminal");
const { exec } = require("child_process");

const client = new Client({
    authStrategy: new LocalAuth(),
});

client.on("qr", qr => {
    console.log("📱 Scan this QR code to login to WhatsApp:");
    qrcode.generate(qr, { small: true });
});

client.on("ready", () => {
    console.log("✅ WhatsApp bot is ready and running!");
});

client.on("message", async message => {
    const number = message.from;
    const text = message.body.trim();

    console.log(`📥 From ${number}: ${text}`);

    exec(`python ai.py "${text}" "${number}"`, (error, stdout, stderr) => {
        if (error) {
            console.error("❌ Python Error:", error.message);
            return;
        }
        if (stderr) {
            console.error("⚠️ Python stderr:", stderr);
            return;
        }

        console.log("🐍 Python stdout:", stdout);  // ✅ Debug

        const reply = stdout.trim();
        if (reply) {
            client.sendMessage(number, reply);
            console.log(`📤 To ${number}: ${reply}`);
        } else {
            console.log("⚠️ No reply returned.");
        }
    });
});

client.initialize();
