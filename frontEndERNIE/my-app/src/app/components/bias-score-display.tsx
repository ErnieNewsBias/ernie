"use client"

import { useEffect, useRef } from "react"
import { Box, Typography } from "@mui/material"

interface BiasScoreDisplayProps {
  isPlaceholder: boolean
  score?: number
  leaning?: string
  confidence?: number | null
}

export default function BiasScoreDisplay({
  isPlaceholder,
  score = 0,
  leaning = "center",
  confidence = null,
}: BiasScoreDisplayProps) {
  const svgRef = useRef<SVGSVGElement>(null)

  // Clamp score between -100 and 100
  const clampedScore = Math.max(-100, Math.min(100, score ?? 0))*10
  const computedLean = clampedScore < 0 ? "Left" : clampedScore > 0 ? "Right" : "center"


  useEffect(() => {
    if (isPlaceholder || !svgRef.current) return

    const needle = svgRef.current.querySelector("#needle")
    if (needle) {
      const rotation = clampedScore * 0.9 // -100 -> -90deg, 0 -> 0deg, +100 -> +90deg
      needle.setAttribute("transform", `rotate(${rotation}, 150, 150)`)
    }
  }, [isPlaceholder, clampedScore])

  if (isPlaceholder) {
    return (
      <Box sx={{ width: "100%", maxWidth: 400, mr: -11 }}>
        <svg width="300" height="200" viewBox="0 0 300 200" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M30,150 A120,120 0 0,1 270,150" stroke="#E5E7EB" strokeWidth="20" strokeLinecap="round" />
          <text x="150" y="180" textAnchor="middle" fill="#9CA3AF" fontSize="14px">
            Bias Score
          </text>
          <text x="60" y="120" textAnchor="middle" fill="#9CA3AF" fontSize="12px">
            Left
          </text>
          <text x="240" y="120" textAnchor="middle" fill="#9CA3AF" fontSize="12px">
            Right
          </text>
          <text x="150" y="90" textAnchor="middle" fill="#D1D5DB" fontSize="24px">
            ?
          </text>
        </svg>
      </Box>
    )
  }

  const gaugeColor = leaning === "Left" ? "#0b52e1" : leaning === "Right" ? "#ce1717" : "#6c757d"

  const leftIntensity = Math.max(0, -clampedScore) / 100
  const rightIntensity = Math.max(0, clampedScore) / 100

  return (
    <Box sx={{ width: "100%", maxWidth: 400, mx: "auto" }}>
      <svg ref={svgRef} width="300" height="200" viewBox="0 0 300 200" fill="none" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor={`rgba(25, 118, 210, ${leftIntensity})`} />
            <stop offset="50%" stopColor="#E5E7EB" />
            <stop offset="100%" stopColor={`rgba(211, 47, 47, ${rightIntensity})`} />
          </linearGradient>
        </defs>

        {/* Gauge background */}
        <path d="M30,150 A120,120 0 0,1 270,150" stroke="url(#gaugeGradient)" strokeWidth="20" strokeLinecap="round" />

        {/* Gauge needle */}
        <line
          id="needle"
          x1="150"
          y1="150"
          x2="150"
          y2="70"
          stroke={gaugeColor}
          strokeWidth="3"
          strokeLinecap="round"
          transform={`rotate(${clampedScore * 0.9}, 150, 150)`}
        />
        <circle cx="150" cy="150" r="10" fill={gaugeColor} />
        <circle cx="150" cy="150" r="5" fill="white" />

        {/* Labels */}
        <text x="60" y="120" textAnchor="middle" fill="#4B5563" fontSize="12px" fontWeight="500">
          Left
        </text>
        <text x="150" y="120" textAnchor="middle" fill="#4B5563" fontSize="12px" fontWeight="500">
          Center
        </text>
        <text x="240" y="120" textAnchor="middle" fill="#4B5563" fontSize="12px" fontWeight="500">
          Right
        </text>

        {/* Score display */}
        <text x="150" y="180" textAnchor="middle" fill="#4B5563" fontSize="14px">
          Bias Score
        </text>
      </svg>

      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mt: 1,
          px: 2,
        }}
      >
        <Box sx={{ flex: 1, textAlign: 'left' }}>
          {confidence !== null && (
            <>
              <Typography variant="body2" color="text.secondary" component="span">
                Confidence:
              </Typography>
              <Typography variant="body2" fontWeight="medium" component="span" sx={{ ml: 0.5 }}>
                {confidence.toFixed(0)}%
              </Typography>
            </>
          )}
        </Box>
        <Box sx={{ flex: 1, textAlign: 'center' }}>
          <Typography variant="h6" fontWeight="bold" component="span" color={gaugeColor}>
            {clampedScore.toFixed(1)}
          </Typography>
          <Typography variant="body2" color="text.secondary" component="span" sx={{ ml: 0.5 }}>
            / 100
          </Typography>
        </Box>
        <Box sx={{ flex: 1, textAlign: 'right' }}>
          <Typography variant="body2" color="text.secondary" component="span">
            Leaning:
          </Typography>
          <Typography
            variant="body2"
            fontWeight="medium"
            component="span"
            color={gaugeColor}
            sx={{ ml: 0.5 }}
          >
            {computedLean}
          </Typography>
        </Box>
      </Box>
    </Box>
  )
}