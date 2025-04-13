"use client"

import type React from "react"
import { useState } from "react"
import {
  Box,
  Typography,
  Card,
  CardContent,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  IconButton,
} from "@mui/material"
import ExpandMoreIcon from "@mui/icons-material/ExpandMore"
import ExpandLessIcon from "@mui/icons-material/ExpandLess"
import DescriptionIcon from "@mui/icons-material/Description"

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`analysis-tabpanel-${index}`}
      aria-labelledby={`analysis-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 2 }}>{children}</Box>}
    </div>
  )
}

interface AIAnalysisData {
  ai_notes: string | null
  bias_quotes: string[] | string | null
  bias_score: Record<string, number> | null
}

interface AIAnalysisProps {
  analysis: AIAnalysisData | null
}

export default function AIAnalysisSection({ analysis }: AIAnalysisProps) {
  const [expanded, setExpanded] = useState(true)
  const [tabValue, setTabValue] = useState(0)

  if (!analysis) {
    return (
      <Typography variant="body2" color="text.secondary" sx={{ mt: 4 }}>
        Analysis data unavailable.
      </Typography>
    )
  }

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue)
  }

  const biasQuoteList = Array.isArray(analysis.bias_quotes)
    ? analysis.bias_quotes
    : typeof analysis.bias_quotes === "string"
    ? analysis.bias_quotes.split("\n").filter((q) => q.trim() !== "")
    : []

  const biasScoreArray = analysis.bias_score ? Object.values(analysis.bias_score) : []
  console.log("biasScoreArray", biasScoreArray)

  return (
    <Box sx={{ mt: 4 }}>
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
        <Typography variant="h6" sx={{ display: "flex", alignItems: "center" }}>
          <DescriptionIcon sx={{ mr: 1 }} />
          AI Analysis
        </Typography>
        <IconButton onClick={() => setExpanded(!expanded)} size="small">
          {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
        </IconButton>
      </Box>

      {expanded && (
        <Box sx={{ width: "100%" }}>
          <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
            <Tabs value={tabValue} onChange={handleTabChange} aria-label="analysis tabs" variant="fullWidth">
              <Tab label="AI Notes" id="analysis-tab-0" aria-controls="analysis-tabpanel-0" />
              <Tab label="Bias Quotes" id="analysis-tab-1" aria-controls="analysis-tabpanel-1" />
            </Tabs>
          </Box>

          <TabPanel value={tabValue} index={0}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="body1" sx={{ whiteSpace: "pre-wrap" }}>
                  {analysis.ai_notes ?? "No AI notes available."}
                </Typography>
              </CardContent>
            </Card>
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            {biasQuoteList.length > 0 ? (
              <Card variant="outlined">
                <CardContent>
                  <List disablePadding>
                    {biasQuoteList.map((quote, index) => {
                      // look up bias score
                      const score = biasScoreArray[index] * 10
                      // determine color
                      let scoreColor = "#6c757d"
                      if (score !== undefined) {
                        scoreColor = score < 0 ? "#0b52e1" : score > 0 ? "#ce1717" : "#6c757d"
                      }
                      return (
                        <ListItem key={index} sx={{ py: 1, alignItems: "flex-start" }}>
                          <Box
                            sx={{
                              mr: 1,
                              mt: 0.5,
                              width: 32,
                              height: 32,
                              display: "flex",
                              justifyContent: "center",
                              alignItems: "center",
                              borderRadius: "50%",
                              backgroundColor: scoreColor,
                              color: "white",
                              fontSize: "0.75rem",
                              flexShrink: 0,
                            }}
                          >
                            {score !== undefined ? score.toFixed(1) : "N/A"}
                          </Box>
                          <ListItemText
                            primary={
                              <Typography variant="body2" sx={{ fontStyle: "italic" }}>
                                {quote}
                              </Typography>
                            }
                          />
                        </ListItem>
                      )
                    })}
                  </List>
                </CardContent>
              </Card>
            ) : (
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="body2" color="text.secondary">
                    No bias quotes identified.
                  </Typography>
                </CardContent>
              </Card>
            )}
          </TabPanel>
        </Box>
      )}
    </Box>
  )
}
