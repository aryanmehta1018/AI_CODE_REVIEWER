import { useState } from "react";
import axios from "axios";
import { Link, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";

function Signup() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] =
    useState("");

  async function handleSignup() {
    try {
      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}/signup`,
        {
          email,
          password,
        }
      );

      toast.success("Signup successful");

      navigate("/");
    } catch (err) {
      console.log(err);
      toast.error("Signup failed");
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1>Create Account</h1>

        <p>
          Start reviewing your code
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

        <button onClick={handleSignup}>
          Signup
        </button>

        <span>
          Already have an account?{" "}
          <Link to="/">
            Login
          </Link>
        </span>
      </div>
    </div>
  );
}

export default Signup;