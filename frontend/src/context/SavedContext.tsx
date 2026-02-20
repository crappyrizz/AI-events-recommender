import { createContext, useContext, useEffect, useState } from "react";
import { getSavedEvents } from "../api/saved";

const USER_ID = 1;

interface SavedContextType {
  savedIds: string[];
  refreshSaved: () => Promise<void>;
}

const SavedContext = createContext<SavedContextType>({
  savedIds: [],
  refreshSaved: async () => {},
});

export function SavedProvider({ children }: { children: React.ReactNode }) {
  const [savedIds, setSavedIds] = useState<string[]>([]);

  async function refreshSaved() {
    const events = await getSavedEvents(USER_ID);
    setSavedIds(events.map((e: any) => e.event_id));
  }

  useEffect(() => {
    refreshSaved();
  }, []);

  return (
    <SavedContext.Provider value={{ savedIds, refreshSaved }}>
      {children}
    </SavedContext.Provider>
  );
}

export function useSaved() {
  return useContext(SavedContext);
}















