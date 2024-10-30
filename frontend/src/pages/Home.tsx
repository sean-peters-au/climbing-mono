import React from "react";
import { Box, Typography, Button } from "@mui/material";
import { useNavigate } from "react-router-dom";
import BoardSelect from "../components/BoardSelect";
import Header from "../components/Header";

const Home: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Box>
      <Header />
      <Box
        sx={{
          height: '80vh', // Full viewport height
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center', // Center vertically
          alignItems: 'center', // Center horizontally
          textAlign: 'center',
          padding: 4,
        }}
      >
        <Box
          sx={{
            display: "inline-flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 5,
            marginTop: 4,
          }}
        >
          <BoardSelect />
          <Typography variant="h4" marginY={2}>
            or
          </Typography>
          <Button
            variant="contained"
            size="large"
            onClick={() => navigate("/walls/new")}
            sx={{
              fontSize: '2rem',
              textTransform: 'none',

            }}
          >
            Create Board
          </Button>
        </Box>
      </Box>
    </Box>
  );
};

export default Home;
