import { useState, useEffect } from "react"
import api from "../../services/api"
import { Users, Car, MapPinned, TrendingUp, Search } from "lucide-react"

export default function AdminDashboard() {
  const [tab, setTab] = useState("drivers") // 'drivers', 'zones', 'students'
  const [driverFilter, setDriverFilter] = useState("all") // 'all', 'pending', 'approved', 'online'
  const [stats, setStats] = useState(null)
  const [drivers, setDrivers] = useState([])
  const [students, setStudents] = useState([])
  const [zones, setZones] = useState([])
  const [newZone, setNewZone] = useState({ name: "", price: "" })
  const [error, setError] = useState("")

  const refresh = () => {
    api.get("/admin/stats").then((res) => setStats(res.data))
    api.get("/admin/drivers").then((res) => setDrivers(res.data))
    api.get("/admin/zones").then((res) => setZones(res.data))
    api.get("/admin/students").then((res) => setStudents(res.data))
  }

  useEffect(() => { refresh() }, [])

  const handleApprove = async (id) => {
    await api.post(`/admin/drivers/${id}/approve`)
    refresh()
  }

  const handleReject = async (id) => {
    const reason = window.prompt("Reason for rejection?") || "Not specified"
    await api.post(`/admin/drivers/${id}/reject`, { reason })
    refresh()
  }

  const handleCreateZone = async (e) => {
    e.preventDefault()
    setError("")
    try {
      await api.post("/admin/zones", { name: newZone.name, price: parseFloat(newZone.price) })
      setNewZone({ name: "", price: "" })
      refresh()
    } catch (err) {
      setError(err.response?.data?.error || "Could not create zone")
    }
  }

  // Filtered lists
  const filteredDrivers = drivers.filter(d => {
    if (driverFilter === "all") return true;
    if (driverFilter === "pending") return d.status === "pending";
    if (driverFilter === "approved") return d.status === "approved";
    if (driverFilter === "online") return d.is_online;
    return true;
  })

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
      <h1 className="font-display font-bold text-3xl mb-8 text-white">System Operations</h1>

      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <StatCard 
            icon={Users} 
            label="Total Students" 
            value={stats.total_students} 
            active={tab === "students"}
            onClick={() => setTab("students")} 
          />
          <StatCard 
            icon={Car} 
            label="Approved Drivers" 
            value={stats.total_drivers} 
            active={tab === "drivers" && driverFilter === "approved"}
            onClick={() => { setTab("drivers"); setDriverFilter("approved"); }} 
          />
          <StatCard 
            icon={MapPinned} 
            label="Drivers Online" 
            value={stats.drivers_online} 
            active={tab === "drivers" && driverFilter === "online"}
            onClick={() => { setTab("drivers"); setDriverFilter("online"); }} 
          />
          <StatCard 
            icon={TrendingUp} 
            label="Total Rides" 
            value={stats.total_rides} 
          />
          <StatCard
            icon={Car}
            label="Active Rides"
            value={stats.active_rides}
          />
          <StatCard
            icon={TrendingUp}
            label="Completed Rides"
            value={stats.completed_rides}
          />
          <StatCard
            icon={TrendingUp}
            label="Platform Revenue"
            value={`₦${stats.platform_revenue.toLocaleString()}`}
          />
          <StatCard
            icon={Users}
            label="Pending Withdrawals"
            value={stats.pending_withdrawals}
          />
        </div>
      )}

      <div className="flex gap-2 mb-6 border-b border-ink-800">
        {["drivers", "students", "zones"].map((t) => (
          <button
            key={t}
            onClick={() => { setTab(t); if(t==="drivers") setDriverFilter("all"); }}
            className={`px-4 py-3 text-sm font-semibold capitalize border-b-2 transition-all ${
              tab === t ? "border-signal text-signal" : "border-transparent text-mist hover:text-white"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      <div className="rounded-card border border-ink-800 bg-ink-900 shadow-glass overflow-hidden">
        {tab === "drivers" && (
          <div className="p-6">
            <div className="flex justify-between items-center mb-6">
               <h2 className="text-xl font-display font-semibold text-white">Driver Management</h2>
               <div className="flex gap-2">
                 {["all", "pending", "approved", "online"].map(f => (
                   <button 
                     key={f} 
                     onClick={() => setDriverFilter(f)}
                     className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${driverFilter === f ? 'bg-signal text-ink-950' : 'bg-ink-800 text-mist hover:text-white'}`}
                   >
                     {f.charAt(0).toUpperCase() + f.slice(1)}
                     {f === "pending" && drivers.filter(d=>d.status==="pending").length > 0 && 
                       <span className="ml-1.5 inline-flex items-center justify-center bg-coral text-white rounded-full h-4 w-4 text-[10px]">
                         {drivers.filter(d=>d.status==="pending").length}
                       </span>
                     }
                   </button>
                 ))}
               </div>
            </div>
            
            <div className="space-y-3">
              {filteredDrivers.length === 0 ? (
                <div className="text-center py-8 text-mist text-sm">No drivers found for this filter.</div>
              ) : (
                filteredDrivers.map((d) => (
                  <div key={d.id} className="flex items-center justify-between bg-ink-950/50 p-4 rounded-xl border border-ink-800/50 hover:border-ink-700 transition-colors">
                    <div>
                      <div className="font-medium text-white text-sm mb-1">{d.full_name}</div>
                      <div className="text-xs text-mist font-mono">
                        {d.vehicle_color} {d.vehicle_make} {d.vehicle_model} · {d.plate_number} · {d.seat_capacity} seats
                      </div>
                      <div className="text-xs text-mist font-mono mt-1">License: {d.license_number}</div>
                    </div>
                    
                    {d.status === "pending" ? (
                      <div className="flex gap-2">
                        <button className="px-3 py-1.5 text-xs font-semibold rounded-lg border border-coral text-coral hover:bg-coral/10" onClick={() => handleReject(d.id)}>Reject</button>
                        <button className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-signal text-ink-950 hover:bg-signal-dim" onClick={() => handleApprove(d.id)}>Approve</button>
                      </div>
                    ) : (
                      <span className={`px-2.5 py-1 text-xs font-medium rounded-md ${d.status === 'approved' ? 'bg-success/10 text-success' : 'bg-coral/10 text-coral'}`}>
                        {d.status.toUpperCase()}
                      </span>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {tab === "students" && (
          <div className="p-6">
            <h2 className="text-xl font-display font-semibold text-white mb-6">Registered Students</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-mist">
                <thead className="border-b border-ink-800 text-xs uppercase bg-ink-950/50">
                  <tr>
                    <th className="px-4 py-3">Full Name</th>
                    <th className="px-4 py-3">Email</th>
                    <th className="px-4 py-3">Student ID</th>
                    <th className="px-4 py-3">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {students.map((s) => (
                    <tr key={s.id} className="border-b border-ink-800/50 hover:bg-ink-800/30 transition-colors">
                      <td className="px-4 py-3 text-white font-medium">{s.full_name}</td>
                      <td className="px-4 py-3">{s.email}</td>
                      <td className="px-4 py-3 font-mono">{s.student_id || "N/A"}</td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 text-[10px] uppercase font-bold rounded ${s.is_verified ? 'bg-success/10 text-success' : 'bg-coral/10 text-coral'}`}>
                          {s.is_verified ? 'Verified' : 'Unverified'}
                        </span>
                      </td>
                    </tr>
                  ))}
                  {students.length === 0 && (
                    <tr><td colSpan="4" className="text-center py-6 text-mist">No students found.</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {tab === "zones" && (
          <div className="p-6">
            <div className="flex justify-between items-center mb-6">
               <h2 className="text-xl font-display font-semibold text-white">Zone Management</h2>
            </div>
            
            <div className="bg-ink-950/50 p-4 rounded-xl border border-ink-800/50 mb-6">
              <div className="font-mono text-xs uppercase tracking-wider text-mist mb-3">Add a New Zone</div>
              <form onSubmit={handleCreateZone} className="flex gap-3 flex-wrap items-end">
                <div className="flex-1 min-w-[200px]">
                  <label className="block text-xs font-medium text-mist mb-1">Zone Name</label>
                  <input type="text" className="w-full rounded-lg border border-ink-700 bg-ink-900 p-2.5 text-sm text-white focus:border-signal focus:outline-none" placeholder="e.g. North Gate" value={newZone.name} onChange={(e) => setNewZone({ ...newZone, name: e.target.value })} required />
                </div>
                <div className="w-32">
                  <label className="block text-xs font-medium text-mist mb-1">Price (₦)</label>
                  <input type="number" className="w-full rounded-lg border border-ink-700 bg-ink-900 p-2.5 text-sm text-white focus:border-signal focus:outline-none" placeholder="e.g. 500" value={newZone.price} onChange={(e) => setNewZone({ ...newZone, price: e.target.value })} required />
                </div>
                <button type="submit" className="px-4 py-2.5 text-sm font-bold bg-signal text-ink-950 rounded-lg hover:bg-signal-dim transition-colors">Add Zone</button>
              </form>
              {error && <p className="text-xs text-coral mt-2">{error}</p>}
            </div>

            <div className="space-y-2">
              {zones.map((z) => (
                <div key={z.id} className="flex items-center justify-between p-4 bg-ink-950/30 rounded-lg border border-ink-800/50">
                  <span className="text-sm text-white font-medium">{z.name}</span>
                  <span className="font-mono text-signal font-bold text-sm">₦{z.price}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function StatCard({ icon: Icon, label, value, active, onClick }) {
  return (
    <div 
      onClick={onClick}
      className={`relative p-5 rounded-card border transition-all cursor-pointer overflow-hidden ${
        active ? "border-signal bg-signal/5 shadow-[0_0_15px_rgba(0,229,255,0.15)]" : "border-ink-800 bg-ink-900 hover:border-ink-700"
      }`}
    >
      {active && <div className="absolute top-0 left-0 w-full h-1 bg-signal" />}
      <Icon size={20} className={`mb-3 ${active ? "text-signal" : "text-mist"}`} />
      <div className="font-display font-bold text-3xl text-white tracking-tight">{value}</div>
      <div className="text-xs text-mist font-medium mt-1">{label}</div>
    </div>
  )
}
