"use client";
import { useState, useEffect } from "react";
import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:3000";

export function useApiHealth() {
  const [isApiUp, setIsApiUp] = useState(true);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        await axios.get(`${API_URL}/health`);
        setIsApiUp(true);
      } catch (error) {
        // Utilisation de _ pour indiquer que le paramètre n'est pas utilisé
        setIsApiUp(false);
        console.error("API is down:", error);
      }
    };

    // Vérifier immédiatement
    checkHealth();

    // Vérifier toutes les 30 secondes
    const interval = setInterval(checkHealth, 30000);

    return () => clearInterval(interval);
  }, []);

  return isApiUp;
}
