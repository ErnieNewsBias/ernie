"use client"

import {
  Box,
  Typography,
  Card,
  CardActionArea,
  CardMedia,
  CardContent,
  Link,
  Button,
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
  onAnalyze: (url: string) => void;
}

export default function SimilarArticlesSection({ articles, onAnalyze }: SimilarArticlesProps) {
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
          pb: 1,
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
              flexShrink: 0,
              justifyContent: 'space-between', // makes room for button
            }}
          >
            <CardActionArea
              component={Link}
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}
            >
              <CardMedia
  component="img"
  height="140"
  image={details.image_url || "https://cdn.discordapp.com/attachments/1360451825450488009/1360743647359799486/BLUEELEPLAHNT.png?ex=67fc3ac6&is=67fae946&hm=9efd46028b480bd0f14e2820e5b6a55a9c74e21406fa2dde09b613498d684fc4&"}
  alt={details.title || 'Article image'}
  sx={{ objectFit: 'cover' }}
  onError={(e: any) => {
    e.target.onerror = null;
    e.target.src = "https://cdn.discordapp.com/attachments/1360451825450488009/1360743647359799486/BLUEELEPLAHNT.png?ex=67fc3ac6&is=67fae946&hm=9efd46028b480bd0f14e2820e5b6a55a9c74e21406fa2dde09b613498d684fc4&";
  }}
/>
              <CardContent sx={{ flexGrow: 1 }}>
                <Typography gutterBottom variant="body1" component="div" sx={{ fontWeight: 500 }}>
                  {details.title || 'Article'}
                </Typography>
              </CardContent>
            </CardActionArea>

            {/* "Analyze This" Button */}
            <Box sx={{ p: 1 }}>
              <Button
                variant="contained"
                size="small"
                fullWidth
                onClick={() => onAnalyze(url)}
              >
                Analyze This
              </Button>
            </Box>
          </Card>
        ))}
      </Box>
    </Box>
  )
}