import React, { useState, useEffect, useCallback } from 'react';
import api from '../../services/api';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

const COLORS = ['#7B61FF', '#00E5FF'];

export default function AdminFinance() {
  const [finance, setFinance] = useState(null);
  const [withdrawals, setWithdrawals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actioning, setActioning] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [financeRes, withdrawalsRes] = await Promise.all([
        api.get('/admin/finance'),
        api.get('/admin/withdrawals?status=pending'),
      ]);
      setFinance(financeRes.data);
      setWithdrawals(withdrawalsRes.data);
    } catch (err) {
      setError('Could not load financial data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const handleAction = async (id, action) => {
    setActioning(id);
    try {
      await api.post(`/admin/withdrawals/${id}/${action}`);
      await load();
    } catch (err) {
      setError(`Failed to ${action} withdrawal`);
    } finally {
      setActioning(null);
    }
  };

  if (loading || !finance) {
    return <div className="mx-auto max-w-6xl p-6 text-mist">{error || 'Loading financial data…'}</div>;
  }

  const pieData = [
    { name: 'Driver Earnings', value: finance.revenue_split.driver_share || 0 },
    { name: 'Platform Fee', value: finance.revenue_split.platform_share || 0 },
  ];
  const pieTotal = pieData[0].value + pieData[1].value || 1;

  return (
    <div className="mx-auto max-w-6xl p-6">
      <h1 className="mb-8 text-3xl font-display font-bold text-white">Financial Dashboard</h1>

      <div className="mb-8 grid gap-6 md:grid-cols-3">
        <div className="rounded-card border border-ink-800 bg-ink-900 p-6 shadow-glass">
          <p className="text-sm font-medium text-mist">Total Platform Revenue</p>
          <h2 className="mt-2 text-3xl font-display font-bold text-signal">₦{finance.total_platform_revenue.toLocaleString()}</h2>
        </div>
        <div className="rounded-card border border-ink-800 bg-ink-900 p-6 shadow-glass">
          <p className="text-sm font-medium text-mist">Total Driver Payouts</p>
          <h2 className="mt-2 text-3xl font-display font-bold text-white">₦{finance.total_driver_payouts.toLocaleString()}</h2>
        </div>
        <div className="rounded-card border border-ink-800 bg-ink-900 p-6 shadow-glass">
          <p className="text-sm font-medium text-mist">Pending Withdrawals</p>
          <h2 className="mt-2 text-3xl font-display font-bold text-coral">
            {finance.pending_withdrawals_count} Request{finance.pending_withdrawals_count === 1 ? '' : 's'}
          </h2>
          <p className="mt-1 text-xs text-mist">₦{finance.pending_withdrawals_amount.toLocaleString()} total</p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <div className="rounded-card border border-ink-800 bg-ink-900 p-6 shadow-glass md:col-span-2">
          <h3 className="mb-6 text-lg font-semibold text-white">Revenue Trend (Last 7 Days)</h3>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={finance.revenue_trend}>
                <defs>
                  <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00E5FF" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#00E5FF" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#2B3545" vertical={false} />
                <XAxis dataKey="label" stroke="#A0ABC0" axisLine={false} tickLine={false} />
                <YAxis stroke="#A0ABC0" axisLine={false} tickLine={false} tickFormatter={(val) => `₦${val}`} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#11151D', border: '1px solid #2B3545', borderRadius: '12px' }}
                />
                <Area type="monotone" dataKey="revenue" stroke="#00E5FF" fillOpacity={1} fill="url(#colorRev)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-card border border-ink-800 bg-ink-900 p-6 shadow-glass">
          <h3 className="mb-6 text-lg font-semibold text-white">Revenue Split (All-Time)</h3>
          <div className="h-[250px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#11151D', border: 'none', borderRadius: '12px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 flex justify-center gap-4 text-sm">
            <div className="flex items-center gap-2">
              <div className="h-3 w-3 rounded-full bg-brand"></div>
              Driver ({Math.round((pieData[0].value / pieTotal) * 100)}%)
            </div>
            <div className="flex items-center gap-2">
              <div className="h-3 w-3 rounded-full bg-signal"></div>
              Platform ({Math.round((pieData[1].value / pieTotal) * 100)}%)
            </div>
          </div>
        </div>
      </div>

      <div className="mt-8 rounded-card border border-ink-800 bg-ink-900 p-6 shadow-glass">
        <h3 className="mb-4 text-lg font-semibold text-white">Pending Withdrawal Requests</h3>
        {withdrawals.length === 0 ? (
          <p className="py-8 text-center text-mist">No pending withdrawal requests</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-mist">
              <thead className="border-b border-ink-800 text-xs uppercase">
                <tr>
                  <th className="px-4 py-3">Driver</th>
                  <th className="px-4 py-3">Amount</th>
                  <th className="px-4 py-3">Account</th>
                  <th className="px-4 py-3">Requested</th>
                  <th className="px-4 py-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {withdrawals.map((w) => (
                  <tr key={w.id} className="border-b border-ink-800/50 hover:bg-ink-800/20">
                    <td className="px-4 py-3 text-white">{w.driver_name || `Driver #${w.driver_id}`}</td>
                    <td className="px-4 py-3">₦{w.amount.toLocaleString()}</td>
                    <td className="px-4 py-3">{w.account_number ? `${w.account_number} (${w.bank_code || ''})` : '—'}</td>
                    <td className="px-4 py-3">{w.created_at ? new Date(w.created_at).toLocaleDateString() : '-'}</td>
                    <td className="px-4 py-3">
                      <div className="flex gap-2">
                        <button
                          disabled={actioning === w.id}
                          onClick={() => handleAction(w.id, 'approve')}
                          className="rounded-lg bg-success/10 px-3 py-1 text-xs font-semibold text-success hover:bg-success/20 disabled:opacity-50"
                        >
                          Approve
                        </button>
                        <button
                          disabled={actioning === w.id}
                          onClick={() => handleAction(w.id, 'reject')}
                          className="rounded-lg bg-coral/10 px-3 py-1 text-xs font-semibold text-coral hover:bg-coral/20 disabled:opacity-50"
                        >
                          Reject
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
