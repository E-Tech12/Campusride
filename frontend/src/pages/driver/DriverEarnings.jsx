import React, { useState, useEffect, useCallback } from 'react';
import WalletCard from '../../components/ui/WalletCard';
import Modal from '../../components/ui/Modal';
import api from '../../services/api';
import {
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar
} from 'recharts';

const TYPE_LABELS = {
  deposit: 'Deposit',
  withdrawal: 'Withdrawal',
  ride_payment: 'Ride Payment',
  ride_refund: 'Ride Refund',
  driver_earning: 'Ride Earning',
  platform_commission: 'Platform Commission',
};

const STATUS_STYLES = {
  success: 'text-success',
  pending: 'text-mist',
  failed: 'text-coral',
};

export default function DriverEarnings() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [isWithdrawOpen, setWithdrawOpen] = useState(false);
  const [amount, setAmount] = useState('');
  const [accountNumber, setAccountNumber] = useState('');
  const [bankCode, setBankCode] = useState('');
  const [accountName, setAccountName] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get('/driver/earnings');
      setData(res.data);
    } catch (err) {
      setError('Could not load earnings data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const handleWithdraw = async () => {
    if (!amount || isNaN(amount) || Number(amount) <= 0) {
      setFormError('Enter a valid amount');
      return;
    }
    setSubmitting(true);
    setFormError(null);
    try {
      await api.post('/driver/withdraw', {
        amount: Number(amount),
        account_number: accountNumber,
        bank_code: bankCode,
        account_name: accountName,
      });
      setWithdrawOpen(false);
      setAmount('');
      setAccountNumber('');
      setBankCode('');
      setAccountName('');
      await load();
    } catch (err) {
      setFormError(err.response?.data?.error || 'Withdrawal request failed');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading || !data) {
    return (
      <div className="mx-auto max-w-5xl p-6 text-mist">
        {error || 'Loading earnings…'}
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl p-4 sm:p-6">
      <h1 className="mb-6 sm:mb-8 text-2xl sm:text-3xl font-display font-bold text-white">Earnings & Wallet</h1>

      <div className="mb-6 grid gap-3 sm:grid-cols-3 sm:gap-4">
        <div className="rounded-card border border-ink-800 bg-ink-900 p-4 shadow-glass">
          <p className="text-xs uppercase text-mist">Today's Earnings</p>
          <p className="mt-1 text-2xl font-bold text-white">₦{data.today_earnings.toLocaleString()}</p>
        </div>
        <div className="rounded-card border border-ink-800 bg-ink-900 p-4 shadow-glass">
          <p className="text-xs uppercase text-mist">Today's Rides</p>
          <p className="mt-1 text-2xl font-bold text-white">{data.today_rides}</p>
        </div>
        <div className="rounded-card border border-ink-800 bg-ink-900 p-4 shadow-glass">
          <p className="text-xs uppercase text-mist">Total Completed Rides</p>
          <p className="mt-1 text-2xl font-bold text-white">{data.total_rides}</p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <div className="md:col-span-1">
          <WalletCard balance={data.balance} type="driver" onWithdraw={() => setWithdrawOpen(true)} />
          {data.pending_withdrawals > 0 && (
            <p className="mt-3 text-xs text-mist">
              {data.pending_withdrawals} withdrawal{data.pending_withdrawals > 1 ? 's' : ''} pending admin approval
            </p>
          )}
        </div>

        <div className="rounded-card border border-ink-800 bg-ink-900 p-6 shadow-glass md:col-span-2">
          <h3 className="mb-6 text-lg font-semibold text-white">Weekly Earnings Overview</h3>
          <div className="h-[250px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.weekly_chart}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2B3545" vertical={false} />
                <XAxis dataKey="label" stroke="#A0ABC0" axisLine={false} tickLine={false} />
                <YAxis stroke="#A0ABC0" axisLine={false} tickLine={false} tickFormatter={(val) => `₦${val}`} />
                <Tooltip
                  cursor={{ fill: '#1B222E' }}
                  contentStyle={{ backgroundColor: '#11151D', border: '1px solid #2B3545', borderRadius: '12px' }}
                />
                <Bar dataKey="earnings" fill="#00E5FF" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="mt-8 rounded-card border border-ink-800 bg-ink-900 p-4 sm:p-6 shadow-glass">
        <h3 className="mb-4 text-lg font-semibold text-white">Recent Transactions</h3>
        {data.recent_transactions.length === 0 ? (
          <p className="py-8 text-center text-mist">No transactions yet</p>
        ) : (
          <>
            {/* Card list on mobile */}
            <div className="space-y-2 sm:hidden">
              {data.recent_transactions.map((t) => (
                <div key={t.id} className="rounded-xl border border-ink-800/60 bg-ink-950/40 p-3">
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-sm text-white font-medium truncate">{t.description || TYPE_LABELS[t.type] || t.type}</span>
                    <span className={`shrink-0 font-semibold text-sm ${t.amount < 0 ? 'text-coral' : 'text-success'}`}>
                      {t.amount < 0 ? '-' : '+'} ₦{Math.abs(t.amount).toLocaleString()}
                    </span>
                  </div>
                  <div className="flex items-center justify-between gap-2 mt-1">
                    <span className="text-xs text-mist">{t.created_at ? new Date(t.created_at).toLocaleDateString() : '-'}</span>
                    <span className={`text-xs ${STATUS_STYLES[t.status] || 'text-mist'}`}>{t.status.charAt(0).toUpperCase() + t.status.slice(1)}</span>
                  </div>
                </div>
              ))}
            </div>

            {/* Table on larger screens */}
            <div className="hidden sm:block overflow-x-auto">
              <table className="w-full text-left text-sm text-mist">
                <thead className="border-b border-ink-800 text-xs uppercase">
                  <tr>
                    <th className="px-4 py-3">Date</th>
                    <th className="px-4 py-3">Description</th>
                    <th className="px-4 py-3">Type</th>
                    <th className="px-4 py-3">Amount</th>
                    <th className="px-4 py-3">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {data.recent_transactions.map((t) => (
                    <tr key={t.id} className="border-b border-ink-800/50 hover:bg-ink-800/20">
                      <td className="px-4 py-3">{t.created_at ? new Date(t.created_at).toLocaleDateString() : '-'}</td>
                      <td className="px-4 py-3">{t.description || TYPE_LABELS[t.type] || t.type}</td>
                      <td className="px-4 py-3">
                        <span className="rounded bg-brand/10 px-2 py-1 text-brand">{TYPE_LABELS[t.type] || t.type}</span>
                      </td>
                      <td className={`px-4 py-3 ${t.amount < 0 ? 'text-coral' : 'text-success'}`}>
                        {t.amount < 0 ? '-' : '+'} ₦{Math.abs(t.amount).toLocaleString()}
                      </td>
                      <td className={`px-4 py-3 ${STATUS_STYLES[t.status] || 'text-mist'}`}>
                        {t.status.charAt(0).toUpperCase() + t.status.slice(1)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>

      <Modal isOpen={isWithdrawOpen} onClose={() => setWithdrawOpen(false)} title="Withdraw Funds">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-mist">Amount (₦)</label>
            <input
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className="mt-1 w-full rounded-xl border border-ink-700 bg-ink-950 p-3 text-white placeholder-ink-600 focus:border-signal focus:outline-none focus:ring-1 focus:ring-signal"
              placeholder="0.00"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-mist">Bank Code</label>
            <input
              type="text"
              value={bankCode}
              onChange={(e) => setBankCode(e.target.value)}
              className="mt-1 w-full rounded-xl border border-ink-700 bg-ink-950 p-3 text-white placeholder-ink-600 focus:border-signal focus:outline-none focus:ring-1 focus:ring-signal"
              placeholder="e.g. 044"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-mist">Account Number</label>
            <input
              type="text"
              value={accountNumber}
              onChange={(e) => setAccountNumber(e.target.value)}
              className="mt-1 w-full rounded-xl border border-ink-700 bg-ink-950 p-3 text-white placeholder-ink-600 focus:border-signal focus:outline-none focus:ring-1 focus:ring-signal"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-mist">Account Name</label>
            <input
              type="text"
              value={accountName}
              onChange={(e) => setAccountName(e.target.value)}
              className="mt-1 w-full rounded-xl border border-ink-700 bg-ink-950 p-3 text-white placeholder-ink-600 focus:border-signal focus:outline-none focus:ring-1 focus:ring-signal"
            />
          </div>
          {formError && <p className="text-sm text-coral">{formError}</p>}
          <button
            onClick={handleWithdraw}
            disabled={submitting}
            className="w-full rounded-xl bg-signal p-3 font-semibold text-ink-950 transition-colors hover:bg-signal-dim disabled:opacity-50"
          >
            {submitting ? 'Submitting…' : 'Request Withdrawal'}
          </button>
        </div>
      </Modal>
    </div>
  );
}
