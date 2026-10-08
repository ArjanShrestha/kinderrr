const toastBox = document.getElementById("toast");
const modal = document.getElementById("modal");
const icebreakerText = document.getElementById("icebreakerText");
const rewindModal = document.getElementById("rewindModal");

function showToast(message) {
    toastBox.textContent = message;
    toastBox.classList.add("show");
    setTimeout(() => toastBox.classList.remove("show"), 2400);
}

function currentMonth() {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
}

// AI matching
const findButton = document.getElementById("findMatches");
if (findButton) {
    findButton.addEventListener("click", async () => {
        const status = document.getElementById("aiStatus");
        findButton.disabled = true;
        findButton.textContent = "✦ AI is thinking...";
        status.textContent = "Finding cross-faculty connections...";
        try {
            const response = await fetch("/api/matches", { method: "POST" });
            const data = await response.json();
            data.matches.forEach(match => {
                const card = document.querySelector(`.card[data-id="${match.id}"]`);
                if (!card) return;
                card.querySelector(".score").textContent = `${match.score}%`;
                card.querySelector(".bar i").style.width = `${match.score}%`;
                card.dataset.reason = match.reason || "Cross-faculty potential and shared interests.";
            });
            status.textContent = data.source === "Qwen2.5" ? "✓ Powered by Qwen2.5" : "✓ Demo mode";
            showToast("AI found your cross-faculty matches ✦");
        } catch (error) {
            status.textContent = "Could not connect to the backend.";
            showToast("Something went wrong. Check Flask.");
        }
        findButton.disabled = false;
        findButton.textContent = "✦ Find my AI matches";
    });
}

// AI icebreakers

document.querySelectorAll(".icebreaker").forEach(button => {
    button.addEventListener("click", async () => {
        const studentId = button.dataset.id;
        modal.classList.remove("hidden");
        icebreakerText.textContent = "Qwen is writing something...";
        try {
            const response = await fetch("/api/icebreaker", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ student_id: studentId })
            });
            const data = await response.json();
            icebreakerText.textContent = data.message;
        } catch (error) {
            icebreakerText.textContent = "Hey! I noticed we have some similar interests. Want to connect?";
        }
    });
});

document.getElementById("closeModal").addEventListener("click", () => modal.classList.add("hidden"));

// Connection buttons

document.querySelectorAll(".connect").forEach(button => {
    button.addEventListener("click", () => {
        const name = button.dataset.name;
        button.textContent = "✓ Connected";
        button.disabled = true;
        showToast(`Connected with ${name} · +10 KU Coins`);
    });
});

// Community/event demo buttons

document.querySelectorAll(".join").forEach(button => {
    button.addEventListener("click", () => {
        button.textContent = "✓ Joined";
        button.disabled = true;
        showToast("Joined! +10 KU Coins");
    });
});

// Copy icebreaker

document.getElementById("copyIcebreaker").addEventListener("click", async () => {
    try {
        await navigator.clipboard.writeText(icebreakerText.textContent);
        showToast("Icebreaker copied!");
    } catch {
        showToast("Select the message and copy it manually.");
    }
});

// -------------------------------------------------
// SHARED MEMORIES
// -------------------------------------------------
const memoryForm = document.getElementById("memoryForm");
const memoryMonth = document.getElementById("memoryMonth");
const memoryGallery = document.getElementById("memoryGallery");
const memoryCount = document.getElementById("memoryCount");
const friendCount = document.getElementById("friendCount");

if (memoryMonth) memoryMonth.value = currentMonth();

function renderMemories(memories) {
    memoryGallery.innerHTML = "";
    if (!memories.length) {
        memoryGallery.innerHTML = `
            <div class="empty-memories">
                <div>📸</div>
                <h3>Your memory wall is empty</h3>
                <p>Upload your first photo above. Your future rewind starts here.</p>
            </div>`;
    } else {
        memories.forEach(memory => {
            const card = document.createElement("article");
            card.className = "memory-card";
            card.innerHTML = `
                <img src="/static/uploads/${memory.filename}" alt="Shared memory">
                <div class="memory-meta"><strong>${escapeHtml(memory.friend)}</strong><span>${escapeHtml(memory.caption)}</span></div>`;
            memoryGallery.appendChild(card);
        });
    }
    memoryCount.textContent = memories.length;
    friendCount.textContent = new Set(memories.map(m => m.friend)).size;
}

function escapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = value || "";
    return div.innerHTML;
}

async function refreshMemories() {
    const month = memoryMonth.value || currentMonth();
    const response = await fetch(`/api/memories?month=${encodeURIComponent(month)}`);
    const data = await response.json();
    renderMemories(data.memories);
    const label = document.getElementById("galleryMonthLabel");
    if (label) label.textContent = `Memory wall · ${month}`;
}

if (memoryMonth) memoryMonth.addEventListener("change", refreshMemories);

if (memoryForm) {
    memoryForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const button = document.getElementById("shareMemory");
        const photo = document.getElementById("memoryPhoto");
        if (!photo.files.length) {
            showToast("Choose a photo first.");
            return;
        }
        button.disabled = true;
        button.textContent = "Saving memory...";
        try {
            const response = await fetch("/api/memories", { method: "POST", body: new FormData(memoryForm) });
            const data = await response.json();
            if (!response.ok) throw new Error(data.error || "Upload failed");
            memoryForm.reset();
            memoryMonth.value = currentMonth();
            await refreshMemories();
            showToast("📸 Memory added! +5 KU Coins");
        } catch (error) {
            showToast(error.message || "Could not save the photo.");
        }
        button.disabled = false;
        button.textContent = "+ Share memory";
    });
}

// -------------------------------------------------
// AI MONTHLY REWIND
// -------------------------------------------------
const createRewind = document.getElementById("createRewind");
const closeRewind = document.getElementById("closeRewind");

function openRewind() {
    rewindModal.classList.remove("hidden");
}

if (closeRewind) closeRewind.addEventListener("click", () => rewindModal.classList.add("hidden"));

if (createRewind) {
    createRewind.addEventListener("click", async () => {
        createRewind.disabled = true;
        createRewind.textContent = "✦ Qwen is creating...";
        try {
            const month = memoryMonth.value || currentMonth();
            const memoriesResponse = await fetch(`/api/memories?month=${encodeURIComponent(month)}`);
            const memoriesData = await memoriesResponse.json();
            const memories = memoriesData.memories;

            const response = await fetch("/api/rewind", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ month })
            });
            const data = await response.json();

            document.getElementById("rewindMonthTitle").textContent = month;
            document.getElementById("rewindTitle").textContent = data.title;
            document.getElementById("rewindStory").textContent = data.story;
            document.getElementById("rewindCount").textContent = `${data.count} memories · ${data.friends ? data.friends.length : 0} friends`;

            const montage = document.getElementById("rewindMontage");
            montage.innerHTML = memories.length
                ? memories.map(m => `<div class="rewind-photo"><img src="/static/uploads/${m.filename}" alt="Rewind memory"><span>${escapeHtml(m.caption)}</span></div>`).join("")
                : `<div class="rewind-placeholder">📸 Add memories to make your rewind more personal.</div>`;

            openRewind();
        } catch (error) {
            showToast("Could not create the rewind. Make sure Flask is running.");
        }
        createRewind.disabled = false;
        createRewind.textContent = "✦ Create AI Rewind";
    });
}

// Load current month memories on page load.
if (memoryGallery) refreshMemories().catch(() => {});
