
const palette = document.getElementById("device-palette");
const canvas = document.getElementById("Canvas");
const ctx = canvas.getContext("2d");

let selectedDevice = null;
let devices = [];
let connections = [];
let isConnectionMode = false;
let firstDevice = null;

let isDragging = false;
let draggedDevice = null;



document.getElementById('troubleshoot-btn').addEventListener('click', function() {
    const problemSelect = document.getElementById('problem-select');
    const selectedProblem = problemSelect.value;

    let troubleshootingCommands = '';

    switch (selectedProblem) {
        case 'missing-routes':
            troubleshootingCommands = `
                show ip route
                show ip protocols
                debug ip rip
                show ip rip database
                show run | include network
            `;
            break;
        case 'rip-version-mismatch':
            troubleshootingCommands = `
                show ip protocols
                debug ip rip
                show run | include version
            `;
            break;
        case 'incorrect-timers':
            troubleshootingCommands = `
                show ip protocols
                show run | include timers
            `;
            break;
        case 'routing-loops':
            troubleshootingCommands = `
                debug ip rip
                show ip route
            `;
            break;
        case 'split-horizon':
            troubleshootingCommands = `
                show ip protocols
                show run | include split-horizon
            `;
            break;
        case 'route-poisoning':
            troubleshootingCommands = `
                debug ip rip
                show ip route
            `;
            break;
        case 'rip-updates-not-received':
            troubleshootingCommands = `
                show ip protocols
                debug ip rip
                show ip interface brief
            `;
            break;
        case 'authentication-issues':
            troubleshootingCommands = `
                show ip protocols
                show run | include authentication
            `;
            break;
        case 'network-overhead':
            troubleshootingCommands = `
                show ip protocols
                debug ip rip
            `;
            break;
        case 'rip-large-networks':
            troubleshootingCommands = `
                show ip protocols
                show ip route
            `;
            break;
        case 'broadcast-multicast':
            troubleshootingCommands = `
                show ip protocols
                show run | include broadcast
            `;
            break;
        case 'convergence-issues':
            troubleshootingCommands = `
                show ip protocols
                debug ip rip
            `;
            break;
        case 'inconsistent-subnet-masks':
            troubleshootingCommands = `
                show ip protocols
                show ip route
            `;
            break;
        case 'passive-interfaces':
            troubleshootingCommands = `
                show ip protocols
                show run | include passive-interface
            `;
            break;
        case 'ttl-issues':
            troubleshootingCommands = `
                debug ip rip
                show ip protocols
            `;
            break;
        default:
            troubleshootingCommands = 'No troubleshooting commands available for this problem.';
    }

    alert(`Troubleshooting Commands:\n${troubleshootingCommands}`);
});

class Device {
    constructor(type, x, y, label) {
        this.type = type;
        this.x = x;
        this.y = y;
        this.label = label;
        this.ipv4 = '';
        this.ipv6 = '';
        this.subnet = '';
        this.protocol = 'none';
    }

    draw(ctx) {
        ctx.beginPath();
        switch (this.type) {
            case 'pc':
                this.drawPC(ctx);
                break;
            case 'router':
                this.drawRouter(ctx);
                break;
            case 'switch':
                this.drawSwitch(ctx);
                break;
        }
        ctx.fillStyle = "#00C3B5";
        ctx.fill();
        ctx.strokeStyle = "#000";
        ctx.stroke();

        // Draw device label below
        ctx.fillStyle = "#fff";
        ctx.font = "14px Arial";
        ctx.textAlign = "center";
        ctx.fillText(this.label, this.x, this.y + 35);
    }

    drawPC(ctx) {
        ctx.rect(this.x - 20, this.y - 20, 40, 40);
    }

    drawRouter(ctx) {
        ctx.arc(this.x, this.y, 20, 0, Math.PI * 2);
    }

    drawSwitch(ctx) {
        ctx.rect(this.x - 30, this.y - 15, 60, 30);
    }
}

class PC extends Device {
    constructor(x, y, label) {
        super('pc', x, y, label);
    }
}

class Router extends Device {
    constructor(x, y, label) {
        super('router', x, y, label);
    }
}

class Switch extends Device {
    constructor(x, y, label) {
        super('switch', x, y, label);
    }
}


// Adjust canvas size
canvas.width = canvas.clientWidth;
canvas.height = canvas.clientHeight;

// Add event listeners for draggable devices
const deviceElements = document.querySelectorAll(".device");
deviceElements.forEach(el => {
    el.addEventListener("dragstart", handleDragStart);
});



function handleDragStart(e) {
    e.dataTransfer.setData("type", e.target.getAttribute("data-type"));
}

// Handle drag over the canvas
canvas.addEventListener("dragover", (e) => e.preventDefault());

// Handle drop on canvas
canvas.addEventListener("drop", (e) => {
const type = e.dataTransfer.getData("type");
const x = e.offsetX;
const y = e.offsetY;

addDevice(type, x, y);
redrawCanvas();
});

// Add device to the canvas
function addDevice(type, x, y) {
let newDevice;
const label = `${type.charAt(0).toUpperCase() + type.slice(1)} ${devices.length + 1}`;

switch (type) {
    case 'pc':
        newDevice = new PC(x, y, label);
        break;
    case 'router':
        newDevice = new Router(x, y, label);
        break;
    case 'switch':
        newDevice = new Switch(x, y, label);
        break;
    default:
        return; // If no valid type is passed, don't add a device
}

devices.push(newDevice);
selectedDevice = newDevice;
redrawCanvas();
}


// Toggle connection mode
document.getElementById("connection-mode-btn").addEventListener("click", () => {
    isConnectionMode = !isConnectionMode;
    document.getElementById("connection-mode-btn").classList.toggle("active", isConnectionMode);
});

// Handle canvas click for device selection and connection mode
canvas.addEventListener("click", (e) => {
    const clickedDevice = findDeviceByPosition(e.offsetX, e.offsetY);
    if (isConnectionMode) {
        if (clickedDevice) {
            if (!firstDevice) {
                firstDevice = clickedDevice;  // Select the first device
            } else {
                addConnection(firstDevice, clickedDevice);  // Connect first and second device
                firstDevice = null;  // Reset after connecting
            }
        }
    } else if (clickedDevice) {
        selectedDevice = clickedDevice;
        openConfigModal(clickedDevice);
    } else {
        selectedDevice = null;
    }
});



// Find device by position
function findDeviceByPosition(x, y) {
    return devices.find(device => {
        const dx = x - device.x;
        const dy = y - device.y;
        return dx * dx + dy * dy <= 400;  // 20px radius for device selection
    });
}

// Redraw canvas with devices and connections
function redrawCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    connections.forEach(connection => drawConnection(connection));
    devices.forEach(device => drawDevice(device));
}

// Draw connection line between devices
function drawConnection(connection) {
    ctx.beginPath();
    ctx.moveTo(connection.device1.x, connection.device1.y);
    ctx.lineTo(connection.device2.x, connection.device2.y);
    ctx.strokeStyle = "#43b581";  
    ctx.lineWidth = 4;
    ctx.stroke();
}

// Draw device on the canvas
// Draw device on the canvas
function drawDevice(device) {
ctx.beginPath();
if (device.type === "pc") {
    // Draw square for PC
    ctx.rect(device.x - 20, device.y - 20, 40, 40);
} else if (device.type === "switch") {
    // Draw rectangle for Switch
    ctx.rect(device.x - 30, device.y - 15, 60, 30);
} else {
    // Default circle for other devices
    ctx.arc(device.x, device.y, 20, 0, Math.PI * 2);
}

ctx.fillStyle = "#00C3B5";  // Device color
ctx.fill();
ctx.strokeStyle = "#000";  // Border color
ctx.stroke();

// Set text properties for device label
ctx.fillStyle = "#fff";  // Text color
ctx.font = "14px Arial";  // Text font and size
ctx.textAlign = "center";  // Center the text
ctx.fillText(device.label, device.x, device.y + 35);  // Display label below the device
}

// Open configuration modal for a device
function openConfigModal(device) {
    const modal = document.getElementById("config-modal");
    document.getElementById("modal-device-label").innerText = device.label;
    document.getElementById("modal-device-ipv4").value = device.ipv4;
    document.getElementById("modal-device-ipv6").value = device.ipv6;
    document.getElementById("modal-subnet-mask").value = device.subnet;
    document.getElementById("modal-routing-protocol").value = device.protocol;
    modal.style.display = "block";
}

// Close configuration modal
document.getElementById("close-modal-btn").addEventListener("click", () => {
    document.getElementById("config-modal").style.display = "none";
});

// Save device configuration from the modal
document.getElementById("modal-device-config-form").addEventListener("submit", (e) => {
    e.preventDefault();

    const device = selectedDevice;
    device.ipv4 = document.getElementById("modal-device-ipv4").value;
    device.ipv6 = document.getElementById("modal-device-ipv6").value;
    device.subnet = document.getElementById("modal-subnet-mask").value;
    device.protocol = document.getElementById("modal-routing-protocol").value;

    document.getElementById("config-modal").style.display = "none";
    redrawCanvas(); 
});

// Add connection between devices
function addConnection(device1, device2) {
    const existingConnection = connections.find(conn =>
        (conn.device1 === device1 && conn.device2 === device2) ||
        (conn.device1 === device2 && conn.device2 === device1)
    );

    if (!existingConnection) {
        connections.push({ device1, device2 });
        redrawCanvas();
    }
    firstDevice = null;  // Reset after connection
}

// Find connection by position for deletion
function findConnectionByPosition(x, y) {
return connections.find(connection => {
    const { device1, device2 } = connection;
    const distanceToLine = pointToLineDistance(x, y, device1.x, device1.y, device2.x, device2.y);
    return distanceToLine < 10;  // Adjusted threshold for clicking accuracy (was 5)
});
}

// Helper function to calculate distance from a point to a line
function pointToLineDistance(px, py, x1, y1, x2, y2) {
    const A = px - x1;
    const B = py - y1;
    const C = x2 - x1;
    const D = y2 - y1;

    const dot = A * C + B * D;
    const lenSq = C * C + D * D;
    const param = lenSq !== 0 ? dot / lenSq : -1;

    let xx, yy;

    if (param < 0) {
        xx = x1;
        yy = y1;
    } else if (param > 1) {
        xx = x2;
        yy = y2;
    } else {
        xx = x1 + param * C;
        yy = y1 + param * D;
    }

    const dx = px - xx;
    const dy = py - yy;
    return Math.sqrt(dx * dx + dy * dy);
}

// Handle delete connection button
document.getElementById("delete-connection-btn").addEventListener("click", () => {
    canvas.addEventListener("click", function deleteConnection(e) {
        const clickedConnection = findConnectionByPosition(e.offsetX, e.offsetY);
        if (clickedConnection) {
            // Remove the clicked connection from the connections array
            connections = connections.filter(conn => conn !== clickedConnection);
            redrawCanvas();  // Redraw canvas after deleting the connection
            alert("Connection deleted!");
        } else {
            alert("No connection clicked to delete.");
        }
        canvas.removeEventListener("click", deleteConnection);
    });
});

// Handle dragging devices
canvas.addEventListener("mousedown", (e) => {
if (isConnectionMode) return; // Prevent dragging in connection mode
const clickedDevice = findDeviceByPosition(e.offsetX, e.offsetY);
if (clickedDevice) {
    isDragging = true;
    draggedDevice = clickedDevice;
}
});

canvas.addEventListener("mousemove", (e) => {
    if (isDragging && draggedDevice) {
        draggedDevice.x = e.offsetX;
        draggedDevice.y = e.offsetY;
        redrawCanvas(); // Redraw the canvas to show the updated position
    }
});

canvas.addEventListener("mouseup", () => {
    isDragging = false;
    draggedDevice = null;
});

// Handle delete device button
document.getElementById("delete-device-btn").addEventListener("click", () => {
    if (selectedDevice) {
        // Remove the selected device from the devices array
        devices = devices.filter(device => device !== selectedDevice);

        // Also remove any associated connections
        connections = connections.filter(connection =>
            connection.device1 !== selectedDevice && connection.device2 !== selectedDevice
        );

        selectedDevice = null;  // Clear selection
        redrawCanvas();  // Redraw canvas after deletion
    } else {
        alert("No device selected to delete.");
    }
});