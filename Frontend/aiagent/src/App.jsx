import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import NewInterview from "./pages/NewInterview";
import Interview from "./pages/Interview";
import History from "./pages/History";
import Results from "./pages/Results";
function App() {
  return (
    <BrowserRouter>

      <Routes>

        <Route
          path="/"
          element={<Navigate to="/login" />}
        />

        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          path="/signup"
          element={<Signup />}
        />

        <Route
          path="/dashboard"
          element={<Dashboard />}
        />
        <Route
        path="/interview"
        element={<NewInterview />}
        />
        <Route
        path="/interview/:interviewId"
       element={<Interview />}
        />
        <Route
        path="/history"
        element={<History />}
        />
        <Route
        path="/results/:interviewId"
        element={<Results/>}
        />

      </Routes>

    </BrowserRouter>
  );
}

export default App;