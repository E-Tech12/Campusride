import React from 'react';

export default function Skeleton({ className = "" }) {
  return (
    <div className={`animate-pulse rounded-md bg-ink-800 ${className}`} />
  );
}
