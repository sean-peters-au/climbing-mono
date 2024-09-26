import { Typography } from '@mui/material';
import React, { useEffect } from 'react';

// Declare the custom element type
declare global {
  namespace JSX {
    interface IntrinsicElements {
      'dotlottie-player': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement> & {
        src: string;
        background: string;
        speed: string;
        style: React.CSSProperties;
        loop: boolean;
        autoplay: boolean;
      };
    }
  }
}

interface LoadingAnimationProps {
  message?: string;
}

const LoadingAnimation: React.FC<LoadingAnimationProps> = ({ message }) => {
  useEffect(() => {
    // Load the dotlottie-player script dynamically
    const script = document.createElement('script');
    script.src = "https://unpkg.com/@dotlottie/player-component@latest/dist/dotlottie-player.mjs";
    script.type = "module";
    document.body.appendChild(script);

    return () => {
      // Clean up the script when the component unmounts
      document.body.removeChild(script);
    };
  }, []);

  return (
    <div style={{ 
      position: 'fixed', 
      top: 0,
      left: 0,
      width: '100vw', 
      height: '100vh', 
      overflow: 'hidden',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      pointerEvents: 'none', // Allow clicks to pass through
      zIndex: 9999 // Ensure it's on top of other elements
    }}>
      <div style={{
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        pointerEvents: 'auto' // Re-enable pointer events for the animation
      }}>
        <dotlottie-player 
          src="https://lottie.host/0c054a4c-507c-467f-b694-41d2b085b2e9/kKP42I3RwH.json" 
          background="transparent" 
          speed="1" 
          style={{ width: '100%', height: '100%' }} 
          loop 
          autoplay
        ></dotlottie-player>
        <Typography 
          variant="h6" 
          style={{ 
            marginTop: '24px', 
            color: 'black', 
            fontSize: '2.5rem', 
            fontWeight: 'bold',
            fontFamily: "'Nunito', sans-serif",
            letterSpacing: '0.5px'
          }}
        >
          {message}
        </Typography>
      </div>
    </div>
  );
};

export default LoadingAnimation;
