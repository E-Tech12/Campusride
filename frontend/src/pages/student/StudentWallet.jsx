import React, { useState, useEffect, useCallback } from 'react';
import WalletCard from '../../components/ui/WalletCard';
import Modal from '../../components/ui/Modal';
import api from '../../services/api';

const TYPE_LABELS = {
  deposit: 'Deposit',
  withdrawal: 'Withdrawal',
  ride_payment: 'Ride Payment',
  ride_refund: 'Ride Refund',
  driver_earning: 'Driver Earning',
  platform_commission: 'Platform Commission',
};

export default function StudentWallet() {
  const [balance, setBalance] = useState(0);
  const [transactions, setTransactions] = useState([]);
  const [loadingData, setLoadingData] = useState(true);
  const [isDepositModalOpen, setDepositModalOpen] = useState(false);
  const [depositAmount, setDepositAmount] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadWallet = useCallback(async () => {
    setLoadingData(true);
    try {
      const [walletRes, txnRes] = await Promise.all([
        api.get('/payments/wallet'),
        api.get('/payments/transactions'),
      ]);
      setBalance(walletRes.data.balance);
      setTransactions(txnRes.data);
    } catch (err) {
      setError('Could not load wallet data');
    } finally {
      setLoadingData(false);
    }
  }, []);

  useEffect(() => {
    loadWallet();
  }, [loadWallet]);

  const handleDeposit = async () => {
    if (!depositAmount || isNaN(depositAmount) || Number(depositAmount) <= 0) {
      setError("Please enter a valid amount");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await api.post('/payments/deposit', { amount: Number(depositAmount) });
      if (res.data.authorization_url) {
        window.location.href = res.data.authorization_url;
      } else {
        setError("Failed to initialize payment");
      }
    } catch (err) {
      setError(err.response?.data?.error || err.message || "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-4xl p-4 sm:p-6">
      <h1 className="mb-8 text-3xl font-display font-bold text-white">My Wallet</h1>

      <div className="grid gap-6 md:grid-cols-2">
        <WalletCard balance={balance} onDeposit={() => setDepositModalOpen(true)} type="student" />

        <div className="rounded-card border border-ink-800 bg-ink-900 p-6 shadow-glass">
          <h3 className="mb-4 text-lg font-semibold text-white">Recent Transactions</h3>
          {loadingData ? (
            <div className="flex h-32 items-center justify-center text-mist">Loading…</div>
          ) : transactions.length === 0 ? (
            <div className="flex h-32 flex-col items-center justify-center text-mist">
              <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mb-2 opacity-50"><path d="M21 12V7H5a2 2 0 0 1 0-4h14v4"/><path d="M3 5v14a2 2 0 0 0 2 2h16v-5"/><path d="M18 12a2 2 0 0 0 0 4h4v-4Z"/></svg>
              <p>No recent transactions</p>
            </div>
          ) : (
            <ul className="max-h-64 space-y-3 overflow-y-auto">
              {transactions.map((t) => (
                <li key={t.id} className="flex items-center justify-between gap-2 flex-wrap border-b border-ink-800 pb-2 last:border-0">
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-white truncate">
                      {TYPE_LABELS[t.type] || t.type}
                    </p>
                    <p className="text-xs text-mist truncate">
                      {t.created_at ? new Date(t.created_at).toLocaleString() : ''} · {t.status}
                    </p>
                  </div>
                  <span className={`shrink-0 font-semibold ${t.amount < 0 ? 'text-coral' : 'text-signal'}`}>
                    {t.amount < 0 ? '-' : '+'}₦{Math.abs(t.amount).toLocaleString()}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      <Modal
        isOpen={isDepositModalOpen}
        onClose={() => setDepositModalOpen(false)}
        title="Deposit Funds"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-mist">Amount (₦)</label>
            <input
              type="number"
              value={depositAmount}
              onChange={(e) => setDepositAmount(e.target.value)}
              className="mt-1 w-full rounded-xl border border-ink-700 bg-ink-950 p-3 text-white placeholder-ink-600 focus:border-signal focus:outline-none focus:ring-1 focus:ring-signal"
              placeholder="0.00"
            />
          </div>
          {error && <p className="text-sm text-coral">{error}</p>}
          <button
            onClick={handleDeposit}
            disabled={loading}
            className="w-full rounded-xl bg-signal p-3 font-semibold text-ink-950 transition-colors hover:bg-signal-dim disabled:opacity-50"
          >
            {loading ? "Processing..." : "Continue to Payment"}
          </button>
        </div>
      </Modal>
    </div>
  );
}
