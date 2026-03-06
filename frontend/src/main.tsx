import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import { SavedProvider } from "./context/SavedContext";
import "leaflet/dist/leaflet.css";
import { UserProvider } from "./context/UserContext";
import './index.css'


ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <UserProvider>
        <SavedProvider>
          <App/>
        </SavedProvider>
      </UserProvider>
    </BrowserRouter>
  </React.StrictMode>
);