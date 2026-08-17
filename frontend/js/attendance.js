/* Three-step attendance flow: QR -> GPS -> camera, then mark attendance. */

requireAuth();

let cameraStream = null;
let scannerStream = null;
let scanFrameHandle = null;

/* ---------------- Step 1: QR ----------------
   Three ways in, all checked by the server against the company code:
     1. The employee scanned the printed poster with their phone camera and
        landed here with ?qr=<code> already in the URL.
     2. They scan the poster from inside this page.
     3. They display the code on screen (fallback when no poster is around).
*/

const scannedFromUrl = new URLSearchParams(window.location.search).get("qr");

if (scannedFromUrl) {
    submitQrCode(scannedFromUrl);
}

async function submitQrCode(code) {
    try {
        await api("/api/qr/verify", {
            method: "POST",
            body: JSON.stringify({ code }),
        });

        stopScanner();
        showError("error", "");
        document.getElementById("qrArea").style.display = "none";
        document.getElementById("qrSuccess").style.display = "block";
        document.getElementById("gpsSection").style.display = "block";
        return true;
    } catch (error) {
        showError("error", error.message);
        return false;
    }
}

/* --- scan the poster with the camera --- */

/* Native detector where it exists (Android Chrome, macOS, ChromeOS),
   bundled jsQR everywhere else. */
function qrDecoder() {
    if (window.BarcodeDetector) {
        try {
            return new window.BarcodeDetector({ formats: ["qr_code"] });
        } catch (error) {
            /* fall through to jsQR */
        }
    }
    return null;
}

// If neither decoder is available, hide the button rather than offering a
// scan that cannot work.
if (!window.BarcodeDetector && typeof window.jsQR !== "function") {
    document.getElementById("scanQR").style.display = "none";
}

document.getElementById("scanQR").addEventListener("click", async function () {
    const video = document.getElementById("scannerPreview");
    const detector = qrDecoder();

    try {
        scannerStream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: "environment" },
        });
    } catch (error) {
        showError("error", "Camera permission is required to scan the QR code.");
        return;
    }

    video.srcObject = scannerStream;
    document.getElementById("scannerWrapper").style.display = "block";
    this.disabled = true;
    showError("error", "");

    scanLoop(detector);
});

async function scanLoop(detector) {
    const video = document.getElementById("scannerPreview");

    if (!scannerStream) return;

    if (video.readyState === video.HAVE_ENOUGH_DATA) {
        const text = detector
            ? await readWithDetector(detector, video)
            : readWithJsQr(video);

        if (text && (await submitQrCode(text))) {
            return; // verified — the flow has moved on to GPS
        }
    }

    scanFrameHandle = requestAnimationFrame(() => scanLoop(detector));
}

async function readWithDetector(detector, video) {
    try {
        const codes = await detector.detect(video);
        return codes.length ? codes[0].rawValue : null;
    } catch (error) {
        return null;
    }
}

function readWithJsQr(video) {
    if (typeof window.jsQR !== "function") return null;

    const canvas = document.getElementById("scannerCanvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const context = canvas.getContext("2d", { willReadFrequently: true });
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    const frame = context.getImageData(0, 0, canvas.width, canvas.height);
    const result = window.jsQR(frame.data, frame.width, frame.height);

    return result ? result.data : null;
}

function stopScanner() {
    if (scanFrameHandle) {
        cancelAnimationFrame(scanFrameHandle);
        scanFrameHandle = null;
    }
    if (scannerStream) {
        scannerStream.getTracks().forEach((track) => track.stop());
        scannerStream = null;
    }
    document.getElementById("scannerWrapper").style.display = "none";
}

document.getElementById("cancelScan").addEventListener("click", () => {
    stopScanner();
    document.getElementById("scanQR").disabled = false;
});

/* --- fallback: show the code on screen --- */

document.getElementById("showQR").addEventListener("click", function () {
    document.getElementById("qrImage").src = apiUrl("/api/qr/image");
    document.getElementById("qrImageWrapper").style.display = "block";
    this.style.display = "none";
});

document.getElementById("verifyQR").addEventListener("click", async function () {
    this.disabled = true;

    try {
        const { code } = await api("/api/qr/payload");
        if (!(await submitQrCode(code))) {
            this.disabled = false;
        }
    } catch (error) {
        this.disabled = false;
        showError("error", error.message);
    }
});

/* ---------------- Step 2: GPS ---------------- */

document.getElementById("verifyGPS").addEventListener("click", function () {
    const button = this;

    if (!navigator.geolocation) {
        showError("error", "Geolocation is not supported by this browser.");
        return;
    }

    button.disabled = true;

    navigator.geolocation.getCurrentPosition(
        () => {
            showError("error", "");
            // Collapse the finished step so only the current one is on screen.
            document.getElementById("gpsSection").style.display = "none";
            document.getElementById("gpsSuccess").style.display = "block";
            document.getElementById("cameraSection").style.display = "block";
        },
        () => {
            button.disabled = false;
            showError("error", "Location access is required to mark attendance.");
        }
    );
});

/* ---------------- Step 3: camera ---------------- */

document.getElementById("openCamera").addEventListener("click", async function () {
    try {
        cameraStream = await navigator.mediaDevices.getUserMedia({ video: true });

        const video = document.getElementById("cameraPreview");
        video.srcObject = cameraStream;
        video.style.display = "block";

        document.getElementById("capturePhoto").style.display = "inline-block";

        this.disabled = true;
        this.innerHTML = '<i class="fa-solid fa-circle-check"></i> Camera Opened';
        showError("error", "");
    } catch (error) {
        showError("error", "Camera permission is required to mark attendance.");
    }
});

document.getElementById("capturePhoto").addEventListener("click", async function () {
    const video = document.getElementById("cameraPreview");
    const canvas = document.getElementById("photoCanvas");

    // The photo stays on the device; only the verification result is sent.
    canvas.getContext("2d").drawImage(video, 0, 0, canvas.width, canvas.height);
    stopCamera();

    this.disabled = true;
    this.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Submitting...';

    try {
        const result = await api("/api/attendance/mark", { method: "POST" });

        document.getElementById("cameraSection").style.display = "none";
        setText(
            "resultTitle",
            result.already_marked
                ? "Attendance Already Recorded"
                : "Attendance Marked Successfully"
        );
        setText(
            "resultDetail",
            `${result.message} (${result.date} at ${result.time} — ${result.status})`
        );
        document.getElementById("attendanceResult").style.display = "block";
    } catch (error) {
        this.disabled = false;
        this.innerHTML =
            '<i class="fa-solid fa-camera-retro"></i> Capture Photo &amp; Submit';
        showError("error", error.message);
    }
});

function stopCamera() {
    if (!cameraStream) return;
    cameraStream.getTracks().forEach((track) => track.stop());
    cameraStream = null;
    document.getElementById("cameraPreview").style.display = "none";
}

// Release both cameras if the user navigates away mid-flow.
window.addEventListener("pagehide", () => {
    stopCamera();
    stopScanner();
});
