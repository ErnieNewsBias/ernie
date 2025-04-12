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
  Grid,
} from "@mui/material"
import BiasScoreDisplay from "@/app/components/bias-score-display"
import AIAnalysisSection from "@/app/components/ai-analysis-section"
import SimilarArticlesSection from "@/app/components/similar-articles-section"
import { ThemeProvider, createTheme } from "@mui/material/styles"
import CssBaseline from "@mui/material/CssBaseline"

// --- Interfaces for API data ---
interface OriginalArticle {
  url: string
  title: string | null
  image_url: string | null
  text_preview: string | null
}

interface AnalysisData {
  bias: number | null
  ai_notes: string | null
  bias_quotes: string | null
  search_query: string | null
}

interface SimilarArticleDetail {
    image_url: string | null
    score: number
    text_preview: string | null
    title: string | null
}

interface SimilarArticlesData {
  [url: string]: SimilarArticleDetail;
}

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
      default: "#95c2ee", // Set this to match your gradient start color
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
  const [apiData, setApiData] = useState<{
    original_article: OriginalArticle | null
    analysis: AnalysisData | null
    similar_articles: SimilarArticlesData | null
  } | null>(null)
  const [apiError, setApiError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    console.log("Form submitted with URL:", url)

    if (!url) {
      console.log("URL is empty, not proceeding")
      return
    }

    let processUrl = url
    if (!url.startsWith("http://") && !url.startsWith("https://")) {
      processUrl = "https://" + url
      setUrl(processUrl)
      console.log("Added https:// prefix to URL:", processUrl)
    }

    setIsLoading(true)
    setAnalysisComplete(false)
    setApiData(null)
    setApiError(null)

    try {
      const apiUrl = `http://127.0.0.1:5000/scrape?url=${encodeURIComponent(processUrl)}`
      console.log("Calling API:", apiUrl)

      const response = await fetch(apiUrl)

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData?.error || `API request failed with status ${response.status}`)
      }

      const data = await response.json()
      console.log("API Response:", data)

      setApiData({
        original_article: data.original_article ?? null,
        analysis: data.analysis ?? null,
        similar_articles: data.similar_articles ?? null,
      })

      setAnalysisComplete(true)
      console.log("Analysis completed for URL:", processUrl)

    } catch (error: any) {
      console.error("API call failed:", error)
      setApiError(error.message || "An unknown error occurred")
      setAnalysisComplete(false)
    } finally {
      setIsLoading(false)
    }
  }

  const determineLeaning = (score: number | null): string => {
    if (score === null) return 'center';
    if (score < 40) return 'left';
    if (score > 60) return 'right';
    return 'center';
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box
        sx={{
          minHeight: "200vh",
          py: 7,
          px: 1,
          background: "linear-gradient(to bottom right,#95c2ee,#f07d7d)",
        }}
      >
        <Container maxWidth="md">
          <Typography variant="h4" component="h1" gutterBottom sx={{ fontFamily: 'Garamond', fontWeight: 'bold', color: 'white',textShadow: '1px 1px 3px rgba(0,0,0,0.6)'}}>
                Article Bias Analyzer
          </Typography>
          <Typography variant="body1" color="white" sx={{ mb: 4 , fontWeight: 'bold' }}><font face = "Garamond">
            Enter a link to any article to analyze its political bias and receive an AI-powered content analysis.
            </font>
          </Typography>

          <Paper elevation={5} sx={{ p: 2, mb: 2 }}>
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
                  error={!!apiError}
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
              {apiError && (
                <Typography color="error" variant="body2" sx={{ mt: 1 }}>
                  Error: {apiError}
                </Typography>
              )}
            </form>
          </Paper>

          <Card elevation = {5} sx={{ mt: 4 }}>
            <CardContent>
              {!analysisComplete && !isLoading && !apiError && (
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

              {apiError && !isLoading && (
                 <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center", py: 4 }}>
                    <Typography color="error" variant="h6">Analysis Failed</Typography>
                    <Typography color="error" variant="body1" sx={{ mt: 1 }}>
                      {apiError}
                    </Typography>
                 </Box>
              )}

              {analysisComplete && !apiError && apiData?.analysis && (
                <Box sx={{ mt: 2, mb: 2 }}>
                  <BiasScoreDisplay
                    isPlaceholder={false}
                    score={apiData.analysis.bias}
                    leaning={determineLeaning(apiData.analysis.bias)}
                    confidence={null}
                  />

                  <AIAnalysisSection analysis={apiData.analysis} />

                   {apiData.similar_articles && Object.keys(apiData.similar_articles).length > 0 && (
                      <SimilarArticlesSection articles={apiData.similar_articles} />
                   )}

                </Box>
              )}
            </CardContent>
          </Card>
        </Container>
      </Box>
    </ThemeProvider>
  )
}
