import { Routes, Route } from "react-router-dom"
import NavBar from "./components/NavBar"
import ProtectedRoute from "./components/ProtectedRoute"

import Landing from "./pages/Landing"
import Login from "./pages/auth/Login"
import Register from "./pages/auth/Register"
import VerifyEmail from "./pages/auth/VerifyEmail"
import ForgotPassword from "./pages/auth/ForgotPassword"
import ResetPassword from "./pages/auth/ResetPassword"

import StudentHome from "./pages/student/StudentHome"
import RideHistory from "./pages/student/RideHistory"
import StudentWallet from "./pages/student/StudentWallet"

import DriverApply from "./pages/driver/DriverApply"
import DriverConsole from "./pages/driver/DriverConsole"
import DriverRouteSetup from "./pages/driver/DriverRouteSetup"
import DriverEarnings from "./pages/driver/DriverEarnings"

import AdminDashboard from "./pages/admin/AdminDashboard"
import AdminFinance from "./pages/admin/AdminFinance"

export default function App() {
  return (
    <div className="min-h-screen flex flex-col bg-ink-950 text-white">
      <NavBar />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/verify-email" element={<VerifyEmail />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />

          <Route
            path="/student"
            element={
              <ProtectedRoute allowedRoles={["student", "driver", "admin"]}>
                <StudentHome />
              </ProtectedRoute>
            }
          />
          <Route
            path="/student/history"
            element={
              <ProtectedRoute allowedRoles={["student", "driver", "admin"]}>
                <RideHistory />
              </ProtectedRoute>
            }
          />
          <Route
            path="/student/wallet"
            element={
              <ProtectedRoute allowedRoles={["student", "driver", "admin"]}>
                <StudentWallet />
              </ProtectedRoute>
            }
          />

          <Route
            path="/driver/apply"
            element={
              <ProtectedRoute allowedRoles={["student"]}>
                <DriverApply />
              </ProtectedRoute>
            }
          />
          <Route
            path="/driver"
            element={
              <ProtectedRoute allowedRoles={["driver"]}>
                <DriverConsole />
              </ProtectedRoute>
            }
          />
          <Route
            path="/driver/route-setup"
            element={
              <ProtectedRoute allowedRoles={["driver"]}>
                <DriverRouteSetup />
              </ProtectedRoute>
            }
          />
          <Route
            path="/driver/earnings"
            element={
              <ProtectedRoute allowedRoles={["driver"]}>
                <DriverEarnings />
              </ProtectedRoute>
            }
          />

          <Route
            path="/admin"
            element={
              <ProtectedRoute allowedRoles={["admin"]}>
                <AdminDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/finance"
            element={
              <ProtectedRoute allowedRoles={["admin"]}>
                <AdminFinance />
              </ProtectedRoute>
            }
          />
        </Routes>
      </main>
    </div>
  )
}
