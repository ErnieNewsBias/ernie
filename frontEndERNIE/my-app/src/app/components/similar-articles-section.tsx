"use client"

import {
  Box,
  Typography,
  Card,
  CardActionArea,
  CardMedia,
  CardContent,
  Link
} from "@mui/material"

interface SimilarArticleDetail {
  image_url: string | null
  score: number
  text_preview: string | null
  title: string | null
}

interface SimilarArticlesData {
  [url: string]: SimilarArticleDetail;
}

interface SimilarArticlesProps {
  articles: SimilarArticlesData;
}

export default function SimilarArticlesSection({ articles }: SimilarArticlesProps) {
  const articleEntries = Object.entries(articles);

  if (articleEntries.length === 0) {
    return null;
  }

  return (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h6" sx={{ mb: 2 }}>
        Similar Articles
      </Typography>

      {/* HORIZONTAL SCROLL CONTAINER */}
      <Box
        sx={{
          display: 'flex',
          overflowX: 'auto',
          flexWrap: 'nowrap',
          gap: 2,
          pb: 1, // padding bottom so scroll looks nicer
          '&::-webkit-scrollbar': {
            height: 8,
          },
          '&::-webkit-scrollbar-thumb': {
            backgroundColor: 'rgba(0, 0, 0, 0.2)',
            borderRadius: 4,
          },
        }}
      >
        {articleEntries.map(([url, details]) => (
          <Card
            key={url}
            sx={{
              minWidth: 250,
              maxWidth: 300,
              display: 'flex',
              flexDirection: 'column',
              flexShrink: 0, // Don't shrink when scrolling
            }}
          >
            <CardActionArea
              component={Link}
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}
            >
              {details.image_url ? (
                <CardMedia
                  component="img"
                  height="140"
                  image={details.image_url}
                  alt={details.title || 'Article image'}
                  sx={{ objectFit: 'cover' }}
                  onError={(e: any) => { e.target.style.display = 'none'; }}
                />
              ) : (
                <Box sx={{ height: 140, display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: 'grey.200' }}>
                  <Typography variant="caption" color="text.secondary">No Image</Typography>
                </Box>
              )}
              <CardContent sx={{ flexGrow: 1 }}>
                <Typography gutterBottom variant="body1" component="div" sx={{ fontWeight: 500 }}>
                  {details.title || 'Article'}
                </Typography>
              </CardContent>
            </CardActionArea>
          </Card>
        ))}
      </Box>
    </Box>
  )
}