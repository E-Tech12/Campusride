import { io } from "socket.io-client"

const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || "http://localhost:5000"

let socket = null

export function getSocket() {
  if (!socket) {
    const token = localStorage.getItem("cr_token")
    socket = io(`${SOCKET_URL}/rides`, {
      auth: { token },
      autoConnect: false,
      transports: ["websocket", "polling"],
    })
  }
  return socket
}

export function connectSocket() {
  const s = getSocket()
  const token = localStorage.getItem("cr_token")
  s.auth = { token }
  if (!s.connected) s.connect()
  return s
}

export function disconnectSocket() {
  if (socket && socket.connected) {
    socket.disconnect()
  }
}
