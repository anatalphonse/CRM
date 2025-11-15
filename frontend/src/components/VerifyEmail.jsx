import { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import axios from "axios";

export default function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");
  const navigate = useNavigate();

  const [message, setMessage] = useState("Verifying your email...");

  useEffect(() => {

    if (!token) {
      setMessage("Token missing in URL.");
      return;
    }

    async function verify() {
      try {
        const response = await axios.get(
          `http://127.0.0.1:8000/auth/verify-email?token=${token}`
        );

        // 👉 Use ONLY backend message
        setMessage(response.data.message);

        // Redirect after 2 seconds
        setTimeout(() => navigate("/login"), 2000);

      } catch (error) {
        if (error.response) {
          // 👉 Use backend error message
          setMessage(error.response.data.detail || "Invalid or expired token");
        } else {
          setMessage("Server not reachable. Try again.");
        }
      }
    }

    verify();
  }, [token, navigate]);

  return (
    <div style={{ textAlign: "center", marginTop: "4rem" }}>
      <h2>{message}</h2>
    </div>
  );
}
