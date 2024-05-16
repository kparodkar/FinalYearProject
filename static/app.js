// Get the canvas element and its context
const canvas = document.getElementById('paintCanvas');
const ctx = canvas.getContext('2d');

// List to store painted pixel coordinates
let paintedPixels = [];

// Flag to track painting state
let isPainting = false;

// Function to start painting
function startPainting(event) {
    isPainting = true;
    paint(event);
}

// Function to end painting
function endPainting() {
    isPainting = false;
    ctx.beginPath(); // Reset the current path
}

// Function to paint on the canvas
function paint(event) {
    if (!isPainting) return;

    // Get the mouse position relative to the canvas
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    // Add the coordinate to the list
    paintedPixels.push({ x, y });

    // Draw a small circle to visualize painting
    ctx.fillStyle = 'red';
    ctx.beginPath();
    ctx.arc(x, y, 2, 0, Math.PI * 2);
    ctx.fill();
}

// Event listeners for mouse actions
canvas.addEventListener('mousedown', startPainting);
canvas.addEventListener('mouseup', endPainting);
canvas.addEventListener('mousemove', paint);

// Function to print painted pixels (for debugging purposes)
function printPaintedPixels() {
    console.log(paintedPixels);
}

// Example: Print painted pixels every 5 seconds
setInterval(printPaintedPixels, 5000);
