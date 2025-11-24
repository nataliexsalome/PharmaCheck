const icon = document.getElementById("statusIcon");
const statusText = document.getElementById("statusText");
const socket = io("http://127.0.0.1:5000", {
  transports: ["websocket"],
});

icon.className = "fa-solid fa-circle-xmark";
statusText.textContent = "Not Connected";

socket.on("connect", () => {
  icon.className = "fa-solid fa-circle-check text-success";
  statusText.textContent = "Server Online";
  statusText.className = "text-success";
});

socket.on("disconnect", () => {
  icon.className = "fa-solid fa-circle-xmark text-danger";
  statusText.textContent = "Server Offline";
  statusText.className = "text-danger";
});

socket.io.on("reconnect_attempt", () => {
  icon.className = "fa-solid fa-spinner fa-spin text-warning";
  statusText.textContent = "Reconnecting to server";
  statusText.className = "text-warning";
});

// socket.io.on("error", (error) => {
//   console.error("Connection error:", error);
// });
