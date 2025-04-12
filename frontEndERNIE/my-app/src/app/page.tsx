"use client"

import type React from "react"

import { useState } from "react"
import {
  Box,
  Container,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Paper,
} from "@mui/material"
import BiasScoreDisplay from "@/app/components/bias-score-display"
import AIAnalysisSection from "@/app/components/ai-analysis-section"
import { ThemeProvider, createTheme } from "@mui/material/styles"
import CssBaseline from "@mui/material/CssBaseline"

// Create a theme
const theme = createTheme({
  palette: {
    primary: {
      main: "#1976d2",
    },
    secondary: {
      main: "#dc004e",
    },
    background: {
      default: "#f5f5f5",
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
  },
})

export default function Home() {
  const [url, setUrl] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [analysisComplete, setAnalysisComplete] = useState(false)
  const [biasData, setBiasData] = useState(null)
  const [aiAnalysis, setAiAnalysis] = useState<{
    summary: string
    keyPoints: string[]
    biasFactors: { factor: string; score: number }[]
  } | null>(null)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    console.log("Form submitted with URL:", url)

    if (!url) {
      console.log("URL is empty, not proceeding")
      return
    }

    // Add basic URL validation
    let processUrl = url
    if (!url.startsWith("http://") && !url.startsWith("https://")) {
      processUrl = "https://" + url
      setUrl(processUrl)
      console.log("Added https:// prefix to URL:", processUrl)
    }

    setIsLoading(true)

    // Simulate API call with timeout
    setTimeout(() => {
      // Generate synthetic data
      const generatedBiasData = {
        score: Math.random() * 100,
        leaning: Math.random() > 0.5 ? "left" : "right",
        confidence: 70 + Math.random() * 25,
      }

      const generatedAnalysis = {
        summary:
          "This article discusses the economic implications of recent policy changes. The author presents multiple viewpoints but tends to favor economic deregulation.",
        keyPoints: [
          "Discusses fiscal policy changes proposed by the administration",
          "Presents arguments from both supporters and critics",
          "Uses emotionally charged language when describing opposition views",
          "Cites studies that predominantly support one perspective",
        ],
        biasFactors: [
          { factor: "Source selection", score: 65 },
          { factor: "Language tone", score: 72 },
          { factor: "Context omission", score: 58 },
          { factor: "Fact presentation", score: 43 },
        ],
      }

      setBiasData(generatedBiasData)
      setAiAnalysis(generatedAnalysis)
      setIsLoading(false)
      setAnalysisComplete(true)
      console.log("Analysis completed for URL:", processUrl)
    }, 2000)
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box
        sx={{
          minHeight: "100vh",
          py: 4,
          px: 2,
          bgcolor: "background.default",
        }}
      >
        <Container maxWidth="md">
          <Typography variant="h4" component="h1" gutterBottom>
            Article Bias Analyzer
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
            Enter a link to any article to analyze its political bias and receive an AI-powered content analysis.
          </Typography>

          <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
            <form onSubmit={handleSubmit}>
              <Box sx={{ display: "flex", flexDirection: { xs: "column", sm: "row" }, gap: 2 }}>
                <TextField
                  fullWidth
                  label="Article URL"
                  variant="outlined"
                  placeholder="https://example.com/article"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === "Enter") {
                      e.preventDefault()
                      handleSubmit(e)
                    }
                  }}
                  helperText={!url ? "Enter a website URL (with or without https://)" : ""}
                />
                <Button
                  variant="contained"
                  color="primary"
                  type="submit"
                  disabled={isLoading || !url}
                  sx={{
                    height: { sm: 56 },
                    minWidth: { xs: "100%", sm: 150 },
                  }}
                  startIcon={isLoading ? <CircularProgress size={20} color="inherit" /> : null}
                >
                  {isLoading ? "Analyzing..." : "Analyze Article"}
                </Button>
              </Box>
            </form>
          </Paper>

          <Card sx={{ mt: 4 }}>
            <CardContent>
              {!analysisComplete && !isLoading && (
                <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center", py: 4 }}>
                  <BiasScoreDisplay isPlaceholder={true} />
                  <Typography color="text.secondary" sx={{ mt: 2 }}>
                    Enter an article URL above to generate a bias analysis
                  </Typography>
                </Box>
              )}

              {isLoading && (
                <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center", py: 6 }}>
                  <CircularProgress size={80} />
                  <Typography variant="body1" sx={{ mt: 3, fontWeight: 500 }}>
                    Analyzing article content and bias...
                  </Typography>
                </Box>
              )}

              {analysisComplete && biasData && aiAnalysis && (
                <Box sx={{ mt: 2, mb: 2 }}>
                  <BiasScoreDisplay
                    isPlaceholder={false}
                    score={biasData.score}
                    leaning={biasData.leaning}
                    confidence={biasData.confidence}
                  />

                  <Box sx={{ mt: 4 }}>
                    <AIAnalysisSection analysis={aiAnalysis} />
                  </Box>
                </Box>
              )}
            </CardContent>
          </Card>
        </Container>
      </Box>
    </ThemeProvider>
  )
}
