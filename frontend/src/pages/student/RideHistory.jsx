import { useEffect, useState } from "react"
import api from "../../services/api"
import Card from "../../components/Card"
import StatusBadge from "../../components/StatusBadge"
import { format } from "date-fns"

export default function RideHistory() {
  const [requests, setRequests] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get("/rides/my-requests").then((res) => {
      setRequests(res.data)
      setLoading(false)
    })
  }, [])

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-6">
      <h1 className="font-display font-bold text-2xl mb-6">My trips</h1>

      {loading && <p className="text-mist text-sm">Loading...</p>}
      {!loading && requests.length === 0 && (
        <Card className="text-center text-mist py-10">No trips yet.</Card>
      )}

      <div className="space-y-3">
        {requests.map((r) => (
          <Card key={r.id} className="flex justify-between items-center">
            <div>
              <div className="font-medium text-sm">{r.zone?.name}</div>
              <div className="text-xs text-mist mt-0.5">
                {r.requested_at && format(new Date(r.requested_at), "MMM d, yyyy · h:mm a")}
              </div>
            </div>
            <div className="text-right">
              <div className="font-mono-num text-signal text-sm mb-1">₦{r.price}</div>
              <StatusBadge status={r.status} />
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
