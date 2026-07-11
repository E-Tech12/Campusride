import React from 'react';
import { createPortal } from 'react-dom';

export default function Modal({ isOpen, onClose, title, children }) {
  if (!isOpen) return null;

  return createPortal(
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
      <div 
        className="absolute inset-0 bg-ink-950/80 backdrop-blur-sm"
        onClick={onClose}
      />
      
      <div className="relative z-10 w-full max-w-lg overflow-hidden rounded-card border border-ink-800 bg-ink-900 shadow-glass animate-in fade-in zoom-in-95 duration-200">
        <div className="flex items-center justify-between border-b border-ink-800 px-6 py-4">
          <h2 className="text-xl font-display font-semibold text-white">{title}</h2>
          <button 
            onClick={onClose}
            className="rounded-full p-2 text-mist hover:bg-ink-800 hover:text-white transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
          </button>
        </div>
        
        <div className="p-6">
          {children}
        </div>
      </div>
    </div>,
    document.body
  );
}
