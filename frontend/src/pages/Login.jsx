import { useState } from "react";
import axios from "axios";
import { useNavigate, Link } from "react-router-dom";
import toast from "react-hot-toast";

function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] =
    useState("");

  async function handleLogin() {
    try {
      const formData =
        new URLSearchParams();

      formData.append(
        "username",
        email
      );

      formData.append(
        "password",
        password
      );

      const response = await axios.post(
        "http://127.0.0.1:8000/login",
        formData,
        {
          headers: {
            "Content-Type":
              "application/x-www-form-urlencoded",
          },
        }
      );

      localStorage.setItem(
        "token",
        response.data.access_token
      );

      toast.success("Login successful");

      navigate("/dashboard");
    } catch (err) {
      console.log(err);
      toast.error("Login failed");
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1>AI Code Reviewer</h1>

        <p>
          Review code with AI instantly
        </p>

        <input
          type="email"
          placeholder="Enter email"
          value={email}
          onChange={(e) =>
            setEmail(e.target.value)
          }
        />

        <input
          type="password"
          placeholder="Enter password"
          value={password}
          onChange={(e) =>
            setPassword(e.target.value)
          }
        />

        <button onClick={handleLogin}>
          Login
        </button>

        <span>
          Don’t have an account?{" "}
          <Link to="/signup">
            Signup
          </Link>
        </span>
      </div>
    </div>
  );
}

export default Login;