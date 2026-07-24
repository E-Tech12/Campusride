import { Routes, Route, Outlet } from "react-router-dom"
import NavBar from "./components/NavBar"
import BottomNav from "./components/BottomNav"
import ProtectedRoute from "./components/ProtectedRoute"

import Landing from "./pages/Landing"
import NotFound from "./pages/NotFound"
import Login from "./pages/auth/Login"
import Register from "./pages/auth/Register"
import VerifyEmail from "./pages/auth/VerifyEmail"
import ForgotPassword from "./pages/auth/ForgotPassword"
import ResetPassword from "./pages/auth/ResetPassword"

import About from "./pages/public/About"
import Safety from "./pages/public/Safety"
import Support from "./pages/public/Support"
import BecomeDriver from "./pages/public/BecomeDriver"
import Contact from "./pages/public/Contact"
import Terms from "./pages/public/Terms"
import Privacy from "./pages/public/Privacy"
import Faq from "./pages/public/Faq"

import StudentHome from "./pages/student/StudentHome"
import RideHistory from "./pages/student/RideHistory"
import StudentWallet from "./pages/student/StudentWallet"
import WalletVerify from "./pages/student/WalletVerify"

import DriverApply from "./pages/driver/DriverApply"
import DriverConsole from "./pages/driver/DriverConsole"
import DriverRouteSetup from "./pages/driver/DriverRouteSetup"
import DriverEarnings from "./pages/driver/DriverEarnings"

import AdminDashboard from "./pages/admin/AdminDashboard"
import AdminFinance from "./pages/admin/AdminFinance"

// Authenticated app shell: the existing top NavBar + BottomNav wraps every
// signed-in dashboard route, exactly as before.
function AppShell() {
  return (
    <div className="min-h-screen flex flex-col bg-ink-950 text-white">
      <NavBar />
      <main className="flex-1 pb-20 md:pb-0">
        <Outlet />
      </main>
      <BottomNav />
    </div>
  )
}

// Public shell: marketing + auth pages each supply their own header/footer
// via <PublicLayout>, so no chrome is added here (this fixes the previous
// bug where Landing rendered a second navbar on top of the global one).
function PublicShell() {
  return <Outlet />
}

export default function App() {
  return (
    <Routes>
      <Route element={<PublicShell />}>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/verify-email" element={<VerifyEmail />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />

        <Route path="/about" element={<About />} />
        <Route path="/safety" element={<Safety />} />
        <Route path="/support" element={<Support />} />
        <Route path="/become-a-driver" element={<BecomeDriver />} />
        <Route path="/contact" element={<Contact />} />
        <Route path="/terms" element={<Terms />} />
        <Route path="/privacy" element={<Privacy />} />
        <Route path="/faq" element={<Faq />} />
        <Route path="*" element={<NotFound />} />
      </Route>

      <Route element={<AppShell />}>
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
        path="/wallet/verify"
        element={<WalletVerify />}
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
      </Route>
    </Routes>
  )
}
