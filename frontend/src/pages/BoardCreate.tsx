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
import API from "../services/api";
import ImageAnnotator from "../components/ImageAnnotator";
import Header from "../components/Header";

type Point = [number, number];

const BoardCreate: React.FC = () => {
  const [name, setName] = useState("");
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [annotations, setAnnotations] = useState<Point[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    setImageFile(file);
    setAnnotations([]);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!imageFile || annotations.length < 3) {
      alert(
        "Please upload an image and annotate at least three points to define the board."
      );
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
                required
                fullWidth
              />
            </Grid>
            <Grid item xs={12}>
              <Button variant="contained" component="label">
                Upload Board Image
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleImageChange}
                  hidden
                  required
                />
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
                disabled={isLoading}
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
