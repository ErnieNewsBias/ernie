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
  Paper,
  IconButton,
} from "@mui/material"
import ExpandMoreIcon from "@mui/icons-material/ExpandMore"
import ExpandLessIcon from "@mui/icons-material/ExpandLess"
import DescriptionIcon from "@mui/icons-material/Description"
import FormatQuoteIcon from '@mui/icons-material/FormatQuote'

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

interface AIAnalysisProps {
  analysis: {
    ai_notes: string | null
    bias_quotes: string | null
  } | null
}

export default function AIAnalysisSection({ analysis }: AIAnalysisProps) {
  const [expanded, setExpanded] = useState(true)
  const [tabValue, setTabValue] = useState(0)

  if (!analysis) {
    return (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 4 }}>
            Analysis data unavailable.
        </Typography>
    );
  }

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue)
  }

  const biasQuoteList = analysis.bias_quotes?.split('\n').filter(q => q.trim() !== '') ?? [];

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
                <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
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
                        {biasQuoteList.map((quote, index) => (
                            <ListItem key={index} sx={{ py: 1, alignItems: 'flex-start' }}>
                                <FormatQuoteIcon sx={{ mr: 1, mt: 0.5, color: 'text.secondary', fontSize: '1.2rem' }} />
                                <ListItemText
                                    primary={
                                        <Typography variant="body2" sx={{ fontStyle: 'italic' }}>
                                            {quote}
                                        </Typography>
                                    }
                                />
                            </ListItem>
                        ))}
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
