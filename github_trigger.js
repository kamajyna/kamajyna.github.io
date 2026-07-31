const fs = require('fs');
if (fs.existsSync('.env')) {
    const envFile = fs.readFileSync('.env', 'utf8');
    envFile.split('\n').forEach(line => {
        const [key, ...vals] = line.split('=');
        if (key && vals.length) {
            process.env[key.trim()] = vals.join('=').trim().replace(/^["']|["']$/g, '');
        }
    });
}
const type = process.argv[2];

if (!type) {
    console.error("Please specify a trigger type (e.g., trigger-dividend or trigger-tech)");
    process.exit(1);
}

const GITHUB_TOKEN = process.env.GITHUB_PAT;
if (!GITHUB_TOKEN) {
    console.error("Error: GITHUB_PAT environment variable is missing.");
    console.error("Please add GITHUB_PAT to your .env file or environment variables.");
    process.exit(1);
}

const REPO = "kamajyna/kamajyna.github.io";

async function triggerWorkflow() {
    console.log(`Triggering GitHub Action (${type}) for ${REPO}...`);
    try {
        const response = await fetch(`https://api.github.com/repos/${REPO}/dispatches`, {
            method: "POST",
            headers: {
                "Accept": "application/vnd.github.v3+json",
                "Authorization": `token ${GITHUB_TOKEN}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                event_type: type
            })
        });

        if (response.ok) {
            console.log(`Successfully triggered ${type}. Status: ${response.status}`);
        } else {
            const errBody = await response.text();
            console.error(`Failed to trigger ${type}. Status: ${response.status}, Error: ${errBody}`);
        }
    } catch (error) {
        console.error("Error triggering workflow:", error);
    }
}

triggerWorkflow();
