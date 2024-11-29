import React from "react";
import { Box, IconButton, Modal, Paper } from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import VideoPlayer from "../VisualPanel/VideoPlayer";

interface RecordingVideoPlayerProps {
  videoUrl: string | null;
  onClose: () => void;
}

const RecordingVideoPlayer: React.FC<RecordingVideoPlayerProps> = ({
  videoUrl,
  onClose,
}) => {
  return (
    <Modal
      open={!!videoUrl}
      onClose={onClose}
      aria-labelledby="recording-playback"
    >
      <Paper
        sx={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          width: "70%",
          maxHeight: "90vh",
          bgcolor: "background.paper",
          boxShadow: 24,
          p: 3,
          m: 2,
          overflow: "hidden",
        }}
      >
        <Box sx={{ position: "relative" }}>
          <IconButton
            onClick={onClose}
            sx={{
              position: "absolute",
              right: -8,
              top: -8,
              bgcolor: "background.paper",
              "&:hover": {
                bgcolor: "action.hover",
              },
              zIndex: 1,
              boxShadow: 2,
            }}
          >
            <CloseIcon />
          </IconButton>
          {videoUrl && <VideoPlayer videoUrl={videoUrl} format="mp4" />}
        </Box>
      </Paper>
    </Modal>
  );
};

export default RecordingVideoPlayer;
