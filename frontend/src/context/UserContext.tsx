import { createContext, useContext, useEffect, useState } from "react";

interface UserContextType {
  userId: string | null;
  setUserEmail: (email: string) => void;
}

const UserContext = createContext<UserContextType>({
  userId: null,
  setUserEmail: () => {},
});

export function UserProvider({ children }: { children: React.ReactNode }) {
  const [userId, setUserId] = useState<string | null>(null);

  // Load from LocalStorage
  useEffect(() => {
    const stored = localStorage.getItem("user_id");
    if (stored) {
      setUserId(stored);
    }
  }, []);

  function setUserEmail(email: string) {
    const id = email.toLowerCase().trim();
    localStorage.setItem("user_id", id);
    setUserId(id);
  }

  return (
    <UserContext.Provider value={{ userId, setUserEmail }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  return useContext(UserContext);
}