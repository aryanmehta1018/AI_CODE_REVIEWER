import { Routes, Route } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import "./App.css";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import MyReviews from "./pages/MyReviews";

function App() {
  return (
    <>
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3000,

          style: {
            background: "#0f172a",
            color: "#fff",
            border: "1px solid rgba(139,92,246,0.4)",
            boxShadow:
              "0 0 20px rgba(139,92,246,0.35)",
          },

          success: {
            iconTheme: {
              primary: "#8b5cf6",
              secondary: "#fff",
            },
          },

          error: {
            iconTheme: {
              primary: "#ef4444",
              secondary: "#fff",
            },
          },
        }}
      />

      <Routes>
        <Route path="/" element={<Login />} />

        <Route
          path="/signup"
          element={<Signup />}
        />

        <Route
          path="/dashboard"
          element={<Dashboard />}
        />
        
        <Route
          path="/my-reviews"
          element={<MyReviews />}
        />
      </Routes>
    </>
  );
}

export default App;