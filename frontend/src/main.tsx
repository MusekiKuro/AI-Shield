import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./shell.css";

// F01 can add these files without changing this entry point.
import.meta.glob("./styles/tokens.css", { eager: true });
import.meta.glob("./styles/base.css", { eager: true });

const root = document.getElementById("root");
if (!root) throw new Error("Application root is missing");

createRoot(root).render(<StrictMode><App /></StrictMode>);
