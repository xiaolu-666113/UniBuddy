const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const chatBox = document.querySelector(".container");
const chatRect = chatBox.getBoundingClientRect();

class Ball {
    constructor(x, y, radius, color) {
        this.x = x;
        this.y = y;
        this.radius = radius;
        this.color = color;
        this.vx = (Math.random() - 0.5) * 2;
        this.vy = (Math.random() - 0.5) * 2;
        this.friction = 0.98;
    }

    draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.fillStyle = this.color;
        ctx.fill();
        ctx.closePath();
    }

    update() {
        this.vx *= this.friction;
        this.vy *= this.friction;
        this.x += this.vx;
        this.y += this.vy;

        // 边界反弹（包含顶部）
        if (this.y + this.radius > canvas.height) {
            this.y = canvas.height - this.radius;
            this.vy *= -1;
        }
        if (this.x + this.radius > canvas.width) {
            this.x = canvas.width - this.radius;
            this.vx *= -1;
        }
        if (this.x - this.radius < 0) {
            this.x = this.radius;
            this.vx *= -1;
        }
        if (this.y - this.radius < 0) {
            this.y = this.radius;
            this.vy *= -1;
        }

        // 聊天框区域反弹处理
        if (
            this.x + this.radius > chatRect.left &&
            this.x - this.radius < chatRect.right &&
            this.y + this.radius > chatRect.top &&
            this.y - this.radius < chatRect.bottom
        ) {
            // 判断反弹方向，简单处理为垂直反弹
            if (this.vx > 0) this.x = chatRect.left - this.radius;
            else this.x = chatRect.right + this.radius;
            this.vx *= -1;
        }

        this.draw();
    }

    applyForce(x, y) {
        let dx = this.x - x;
        let dy = this.y - y;
        let dist = Math.sqrt(dx * dx + dy * dy);
        let force = 300 / (dist + 50);
        let angle = Math.atan2(dy, dx);
        this.vx += Math.cos(angle) * force;
        this.vy += Math.sin(angle) * force;
    }
}

const colors = ["#FF6F61", "#BA68C8", "#4DB6AC", "#FFD54F", "#64B5F6"];
let balls = [];
for (let i = 0; i < 25; i++) {
    let radius = 12;
    let x = Math.random() * canvas.width;
    let y = Math.random() * canvas.height;
    balls.push(new Ball(x, y, radius, colors[Math.floor(Math.random() * colors.length)]));
}

function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (let b of balls) b.update();
    requestAnimationFrame(animate);
}
animate();

canvas.addEventListener("click", (e) => {
    balls.forEach(b => b.applyForce(e.clientX, e.clientY));
    showPulse(e.clientX, e.clientY);
});

function showPulse(x, y) {
    let radius = 0;
    let opacity = 1;
    function pulse() {
        ctx.beginPath();
        ctx.arc(x, y, radius, 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(0,0,0,${opacity})`;
        ctx.lineWidth = 2;
        ctx.stroke();
        ctx.closePath();
        radius += 5;
        opacity -= 0.03;
        if (opacity > 0) requestAnimationFrame(pulse);
    }
    pulse();
}

window.addEventListener("resize", () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
});