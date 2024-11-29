import React, { createContext, useState, FC, useEffect } from 'react';
import { Wall, Hold, Route, HoldAnnotationPlayback, HoldVectorPlayback, DrawnData, VisualMode, KinematicsPlayback } from '../../types';

interface BoardViewContextProps {
  wall: Wall;
  holds: Hold[];
  selectedTab: number;
  setSelectedTab: (tab: number) => void;
  visualMode: VisualMode;
  setVisualMode: (mode: VisualMode) => void;
  showAllHolds: boolean;
  setShowAllHolds: (value: boolean) => void;
  selectedHolds: string[];
  setSelectedHolds: (holds: string[]) => void;
  handleHoldClick: (holdId: string) => void;
  playbackVectors: HoldVectorPlayback[];
  setPlaybackVectors: (vectors: HoldVectorPlayback[]) => void;
  playbackAnnotations: HoldAnnotationPlayback[];
  setPlaybackAnnotations: (annotations: HoldAnnotationPlayback[]) => void;
  playbackFrames: number;
  setPlaybackFrames: (frames: number) => void;
  selectedRoute: Route | null;
  setSelectedRoute: (route: Route | null) => void;
  isPlaying: boolean;
  setIsPlaying: (value: boolean) => void;
  currentFrame: number;
  setCurrentFrame: (value: number) => void;
  frameRate: number;
  isDrawing: boolean;
  setIsDrawing: (value: boolean) => void;
  drawnData: DrawnData | null;
  setDrawnData: (data: DrawnData | null) => void;
  playbackKinematics: KinematicsPlayback | null;
  setPlaybackKinematics: (data: KinematicsPlayback | null) => void;
}

export const BoardViewContext = createContext<BoardViewContextProps | undefined>(undefined);

interface BoardViewProviderProps {
  wall: Wall;
  children: React.ReactNode;
}

export const BoardViewProvider: FC<BoardViewProviderProps> = ({ wall, children }) => {
  const [selectedTab, setSelectedTab] = useState<number>(0);
  const [visualMode, setVisualMode] = useState<VisualMode>('2D');
  const [showAllHolds, setShowAllHolds] = useState<boolean>(false);
  const [selectedHolds, setSelectedHolds] = useState<string[]>([]);
  const [playbackVectors, setPlaybackVectors] = useState<HoldVectorPlayback[]>([]);
  const [playbackAnnotations, setPlaybackAnnotations] = useState<HoldAnnotationPlayback[]>([]);
  const [playbackFrames, setPlaybackFrames] = useState<number>(0);
  const [selectedRoute, setSelectedRoute] = useState<Route | null>(null);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [currentFrame, setCurrentFrame] = useState<number>(0);
  const frameRate = 100; // Hz
  const [isDrawing, setIsDrawing] = useState<boolean>(false);
  const [drawnData, setDrawnData] = useState<DrawnData | null>(null);
  const [playbackKinematics, setPlaybackKinematics] = useState<KinematicsPlayback | null>(null);

  useEffect(() => {
    let lastFrameTime = 0;
    let animationFrameId: number;
    const frameInterval = 1000 / frameRate; // Convert Hz to ms between frames

    const animate = (timestamp: number) => {
      if (!lastFrameTime) lastFrameTime = timestamp;
      
      const deltaTime = timestamp - lastFrameTime;
      
      if (deltaTime >= frameInterval) {
        setCurrentFrame((prevFrame) => {
          const newFrame = prevFrame + 1;
          if (newFrame >= playbackFrames) {
            setIsPlaying(false);
            return playbackFrames;
          }
          return newFrame;
        });
        lastFrameTime = timestamp;
      }

      if (isPlaying) {
        animationFrameId = requestAnimationFrame(animate);
      }
    };

    if (isPlaying) {
      animationFrameId = requestAnimationFrame(animate);
    }

    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [isPlaying, playbackFrames, frameRate]);

  const handleHoldClick = (holdId: string) => {
    setSelectedRoute(null);
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
        visualMode,
        setVisualMode,
        showAllHolds,
        setShowAllHolds,
        selectedHolds: selectedHolds,
        setSelectedHolds,
        handleHoldClick,
        playbackVectors,
        setPlaybackVectors,
        playbackAnnotations,
        setPlaybackAnnotations,
        playbackFrames,
        setPlaybackFrames,
        selectedRoute,
        setSelectedRoute,
        isPlaying,
        setIsPlaying,
        currentFrame,
        setCurrentFrame,
        frameRate,
        isDrawing,
        setIsDrawing,
        drawnData,
        setDrawnData,
        playbackKinematics,
        setPlaybackKinematics,
      }}
    >
      {children}
    </BoardViewContext.Provider>
  );
};
