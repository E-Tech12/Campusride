import React from 'react';

export default function WalletCard({ balance, onDeposit, onWithdraw, type = "student" }) {
  return (
    <div className="relative overflow-hidden rounded-card border border-ink-800 bg-ink-900 p-6 shadow-glass">
      {/* Decorative gradient */}
      <div className="absolute -right-20 -top-20 h-40 w-40 rounded-full bg-brand/20 blur-3xl" />
      <div className="absolute -bottom-20 -left-20 h-40 w-40 rounded-full bg-signal/10 blur-3xl" />
      
      <div className="relative z-10">
        <p className="text-sm font-medium text-mist">Available Balance</p>
        <h2 className="mt-2 text-4xl font-display font-bold text-white">
          ₦{balance?.toFixed(2) || "0.00"}
        </h2>
        
        <div className="mt-6 flex gap-3">
          <button 
            onClick={onDeposit}
            className="flex-1 rounded-xl bg-signal px-4 py-2.5 text-sm font-semibold text-ink-950 shadow-glow transition-all hover:bg-signal-dim"
          >
            Deposit Funds
          </button>
          
          {type === "driver" && (
            <button
              onClick={onWithdraw}
              className="flex-1 rounded-xl border border-ink-700 bg-ink-800 px-4 py-2.5 text-sm font-semibold text-white transition-all hover:bg-ink-700"
            >
              Withdraw
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
