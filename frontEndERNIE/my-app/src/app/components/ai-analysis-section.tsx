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
  LinearProgress,
  Divider,
  Alert,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Avatar,
} from "@mui/material"
import ExpandMoreIcon from "@mui/icons-material/ExpandMore"
import ExpandLessIcon from "@mui/icons-material/ExpandLess"
import DescriptionIcon from "@mui/icons-material/Description"
import BarChartIcon from "@mui/icons-material/BarChart"
import WarningAmberIcon from "@mui/icons-material/WarningAmber"

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

interface BiasFactorType {
  factor: string
  score: number
}

interface AIAnalysisProps {
  analysis: {
    summary: string
    keyPoints: string[]
    biasFactors: BiasFactorType[]
  }
}

export default function AIAnalysisSection({ analysis }: AIAnalysisProps) {
  const [expanded, setExpanded] = useState(true)
  const [tabValue, setTabValue] = useState(0)

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue)
  }

  const getScoreColor = (score: number) => {
    if (score < 40) return "success"
    if (score < 70) return "warning"
    return "error"
  }

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
              <Tab label="Summary" id="analysis-tab-0" aria-controls="analysis-tabpanel-0" />
              <Tab label="Key Points" id="analysis-tab-1" aria-controls="analysis-tabpanel-1" />
              <Tab label="Bias Factors" id="analysis-tab-2" aria-controls="analysis-tabpanel-2" />
            </Tabs>
          </Box>

          <TabPanel value={tabValue} index={0}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="body1">{analysis.summary}</Typography>
              </CardContent>
            </Card>
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            <Card variant="outlined">
              <CardContent>
                <List>
                  {analysis.keyPoints.map((point, index) => (
                    <ListItem key={index} sx={{ py: 1 }}>
                      <ListItemIcon sx={{ minWidth: 36 }}>
                        <Avatar
                          sx={{
                            width: 24,
                            height: 24,
                            bgcolor: "primary.main",
                            fontSize: 14,
                          }}
                        >
                          {index + 1}
                        </Avatar>
                      </ListItemIcon>
                      <ListItemText primary={point} />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </TabPanel>

          <TabPanel value={tabValue} index={2}>
            <Card variant="outlined">
              <CardContent>
                <Box sx={{ mb: 2, display: "flex", justifyContent: "space-between" }}>
                  <Typography variant="body2" color="text.secondary">
                    Factor
                  </Typography>
                  <Box sx={{ display: "flex", alignItems: "center" }}>
                    <Typography variant="body2" color="text.secondary" sx={{ mr: 1 }}>
                      Bias Level
                    </Typography>
                    <BarChartIcon fontSize="small" color="action" />
                  </Box>
                </Box>

                {analysis.biasFactors.map((factor, index) => (
                  <Box key={index} sx={{ mb: 2 }}>
                    <Box sx={{ display: "flex", justifyContent: "space-between", mb: 0.5 }}>
                      <Typography variant="body2" fontWeight="medium">
                        {factor.factor}
                      </Typography>
                      <Typography variant="body2" fontWeight="medium">
                        {factor.score}/100
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={factor.score}
                      color={getScoreColor(factor.score as any)}
                      sx={{ height: 8, borderRadius: 4 }}
                    />
                  </Box>
                ))}

                <Divider sx={{ my: 2 }} />

                <Alert severity="warning" icon={<WarningAmberIcon />} sx={{ bgcolor: "transparent" }}>
                  <Typography variant="body2">
                    Bias factors are calculated based on language patterns, source diversity, contextual framing, and
                    comparison with a diverse corpus of political content.
                  </Typography>
                </Alert>
              </CardContent>
            </Card>
          </TabPanel>
        </Box>
      )}
    </Box>
  )
}
