import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Grid,
  Box,
  Typography,
  TextField,
  Button,
  CircularProgress,
} from "@mui/material";
import { getCameraPhoto } from "../services/betaboard-camera/api";
import API from "../services/betaboard-backend/api";
import ImageAnnotator from "../components/ImageAnnotator";
import Header from "../components/Header";

type Point = [number, number];

const BoardCreate: React.FC = () => {
  const [name, setName] = useState("");
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [annotations, setAnnotations] = useState<Point[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleCapturePhoto = async () => {
    try {
      const imageBlob = await getCameraPhoto();
      const file = new File([imageBlob], 'captured_photo.jpg', { type: 'image/jpeg' });
      setImageFile(file);
      setAnnotations([]);
    } catch (error) {
      console.error("Error capturing photo:", error);
      alert("Failed to capture photo. Please try again.");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!name.trim()) {
      alert("Please enter a board name");
      return;
    }

    if (!imageFile) {
      alert("Please capture or upload an image");
      return;
    }

    if (annotations.length < 3) {
      alert("Please annotate at least three points to define the board");
      return;
    }

    setIsLoading(true);

    const reader = new FileReader();
    reader.readAsDataURL(imageFile);
    reader.onloadend = async () => {
      const base64Image = reader.result?.toString().split(",")[1];

      try {
        await API.post("/wall", {
          name,
          image: base64Image,
          wall_annotations: annotations,
        });

        navigate("/");
      } catch (error) {
        console.error("Error creating board:", error);
        alert("Failed to create board. Please try again.");
      } finally {
        setIsLoading(false);
      }
    };
  };

  const handleResetAnnotations = () => {
    setAnnotations([]);
  };

  return (
    <>
      <Header />
      <Box sx={{ padding: 4 }}>
        <Typography variant="h1" gutterBottom>
          Create New Board
        </Typography>
        <form onSubmit={handleSubmit}>
          <Grid container spacing={4}>
            <Grid item xs={12}>
              <TextField
                label="Board Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                fullWidth
              />
            </Grid>
            <Grid item xs={12}>
              <Button 
                variant="contained" 
                onClick={handleCapturePhoto}
                sx={{ marginRight: 2 }}
              >
                Capture Photo
              </Button>
            </Grid>
            {imageFile && (
              <>
                <Grid item xs={12}>
                  <Typography variant="body1">
                    Click on the image to annotate the board's polygon. Click
                    "Finish Annotation" when done.
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <ImageAnnotator
                    imageFile={imageFile}
                    annotations={annotations}
                    setAnnotations={setAnnotations}
                  />
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="body2">
                    {annotations.length} point(s) added.
                  </Typography>
                  <Button variant="outlined" onClick={handleResetAnnotations}>
                    Reset Annotations
                  </Button>
                </Grid>
              </>
            )}
            <Grid item xs={12}>
              <Button
                type="submit"
                variant="contained"
                disabled={isLoading || !imageFile || !name.trim() || annotations.length < 3}
                startIcon={isLoading ? <CircularProgress size={20} /> : null}
              >
                {isLoading ? "Creating Board..." : "Create Board"}
              </Button>
            </Grid>
          </Grid>
        </form>
      </Box>
    </>
  );
};

export default BoardCreate;
