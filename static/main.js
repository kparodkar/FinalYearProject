const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
let painting = false;
let brushColor = document.getElementById('brush-color').value;
let brushSize = document.getElementById('brush-size').value;
let brushType = document.querySelector('input[name="brush"]:checked').value;

document.getElementById('brush-color').addEventListener('change', (e) => {
    brushColor = e.target.value;
});

document.getElementById('brush-size').addEventListener('input', (e) => {
    brushSize = e.target.value;
    document.getElementById('brush-size-label').innerText = brushSize;
});

document.querySelectorAll('input[name="brush"]').forEach((elem) => {
    elem.addEventListener('change', (e) => {
        brushType = e.target.value;
    });
});

canvas.addEventListener('mousedown', () => {
    painting = true;
});

canvas.addEventListener('mouseup', () => {
    painting = false;
    ctx.beginPath();
});

canvas.addEventListener('mousemove', draw);

function draw(e) {
    if (!painting) return;
    ctx.lineWidth = brushSize;
    ctx.lineCap = 'round';
    ctx.strokeStyle = brushColor;

    switch (brushType) {
        case 'round':
            ctx.lineCap = 'round';
            break;
        case 'slash':
            ctx.lineCap = 'butt';
            break;
        case 'diamond':
            ctx.lineCap = 'square';
            break;
        case 'fan':
            drawFan(e);
            return;
        case 'oil':
            drawOilBrush(e);
            return;
        case 'watercolor':
            drawWatercolorBrush(e);
            return;
        case 'smudge':
            smudge(e);
            return;
    }

    ctx.lineTo(e.clientX - canvas.offsetLeft, e.clientY - canvas.offsetTop);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(e.clientX - canvas.offsetLeft, e.clientY - canvas.offsetTop);
}

function drawFan(e) {
    const numLines = 10;
    const radius = 30;
    const centerX = e.clientX - canvas.offsetLeft;
    const centerY = e.clientY - canvas.offsetTop;

    for (let angle = 180; angle < 360; angle += 180 / numLines) {
        const endX = centerX + radius * Math.cos((angle * Math.PI) / 180);
        const endY = centerY + radius * Math.sin((angle * Math.PI) / 180);
        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.lineTo(endX, endY);
        ctx.stroke();
    }
}

function drawOilBrush(e) {
    const radius = brushSize / 2;
    const centerX = e.clientX - canvas.offsetLeft;
    const centerY = e.clientY - canvas.offsetTop;
    const numStrokes = 10;

    for (let i = 0; i < numStrokes; i++) {
        const randX = centerX + Math.random() * radius - radius / 2;
        const randY = centerY + Math.random() * radius - radius / 2;
        ctx.fillStyle = getRandomColor();
        ctx.beginPath();
        ctx.arc(randX, randY, radius, 0, 2 * Math.PI);
        ctx.fill();
    }
}

function drawWatercolorBrush(e) {
    const x = e.clientX - canvas.offsetLeft;
    const y = e.clientY - canvas.offsetTop;
    const size = brushSize;
    ctx.fillStyle = brushColor;
    ctx.beginPath();
    ctx.arc(x, y, size, 0, 2 * Math.PI);
    ctx.fill();
}

function smudge(e) {
    // Implementation for smudge effect
    // This can be more complex depending on the requirements
}

function getRandomColor() {
    const r = Math.floor(Math.random() * 256);
    const g = Math.floor(Math.random() * 256);
    const b = Math.floor(Math.random() * 256);
    return `rgb(${r},${g},${b})`;
}

function clearCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}

function saveImage() {
    const imageData = canvas.toDataURL();
    fetch('/save', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ imageData: imageData }),
    })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}
