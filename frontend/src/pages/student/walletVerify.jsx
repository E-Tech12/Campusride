import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import api from "../../services/api";

export default function WalletVerify() {
  const [params] = useSearchParams();
  const navigate = useNavigate();

  const [status, setStatus] = useState("loading");
  const [message, setMessage] = useState("Verifying your payment...");

  useEffect(() => {
    const verify = async () => {
      const reference = params.get("reference");

      if (!reference) {
        navigate("/student/wallet");
        return;
      }

      try {
        await api.get(`/payments/verify/${reference}`);

        setStatus("success");
        setMessage("Your wallet has been funded successfully.");

        setTimeout(() => {
          navigate("/student/wallet");
        }, 2500);
      } catch (error) {
        console.error(error);

        setStatus("error");
        setMessage("Payment verification failed.");

        setTimeout(() => {
          navigate("/student/wallet");
        }, 3000);
      }
    };

    verify();
  }, [params, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-ink-950 px-4">
      <div className="w-full max-w-md rounded-3xl border border-ink-800 bg-ink-900 p-8 shadow-2xl text-center">
        {status === "loading" && (
          <>
            <div className="mx-auto mb-6 h-16 w-16 animate-spin rounded-full border-4 border-signal border-t-transparent"></div>
            <h2 className="text-2xl font-bold text-white">
              Verifying Payment
            </h2>
          </>
        )}

        {status === "success" && (
          <>
            <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-green-500/20">
              <span className="text-3xl text-green-400">✓</span>
            </div>
            <h2 className="text-2xl font-bold text-white">
              Payment Successful
            </h2>
          </>
        )}

        {status === "error" && (
          <>
            <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-red-500/20">
              <span className="text-3xl text-red-400">✕</span>
            </div>
            <h2 className="text-2xl font-bold text-white">
              Verification Failed
            </h2>
          </>
        )}

        <p className="mt-4 text-mist">
          {message}
        </p>
      </div>
    </div>
  );
}