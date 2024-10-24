import React, { createContext, useState, FC } from 'react';
import { SensorReadingFrame, Wall, Hold, Route } from '../../types';

interface BoardViewContextProps {
  wall: Wall;
  holds: Hold[];
  selectedTab: number;
  setSelectedTab: (tab: number) => void;
  showAllHolds: boolean;
  toggleShowAllHolds: () => void;
  selectedHolds: string[];
  setSelectedHolds: (holds: string[]) => void;
  handleHoldClick: (holdId: string) => void;
  playbackData: SensorReadingFrame[] | null;
  setPlaybackData: (data: SensorReadingFrame[] | null) => void;
  selectedRoute: Route | null;
  setSelectedRoute: (route: Route | null) => void;
}

export const BoardViewContext = createContext<BoardViewContextProps | undefined>(undefined);

interface BoardViewProviderProps {
  wall: Wall;
  children: React.ReactNode;
}

export const BoardViewProvider: FC<BoardViewProviderProps> = ({ wall, children }) => {
  const [selectedTab, setSelectedTab] = useState<number>(0);
  const [showAllHolds, setShowAllHolds] = useState<boolean>(false);
  const [selectedHolds, setSelectedHolds] = useState<string[]>([]);
  const [playbackData, setPlaybackData] = useState<SensorReadingFrame[] | null>(null);
  const [selectedRoute, setSelectedRoute] = useState<Route | null>(null);

  const toggleShowAllHolds = () => {
    setShowAllHolds((prev) => !prev);
  };

  const handleHoldClick = (holdId: string) => {
    setSelectedHolds((prevHolds) =>
      prevHolds.includes(holdId)
        ? prevHolds.filter((id) => id !== holdId)
        : [...prevHolds, holdId]
    );
  };

  return (
    <BoardViewContext.Provider
      value={{
        wall,
        holds: wall.holds,
        selectedTab,
        setSelectedTab,
        showAllHolds,
        toggleShowAllHolds,
        selectedHolds: selectedHolds,
        setSelectedHolds,
        handleHoldClick,
        playbackData,
        setPlaybackData,
        selectedRoute,
        setSelectedRoute,
      }}
    >
      {children}
    </BoardViewContext.Provider>
  );
};
