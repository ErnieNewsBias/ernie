"use client"

import {
    Box,
    Typography,
    Grid,
    Card,
    CardActionArea,
    CardMedia,
    CardContent,
    Link, // Use Link for clickable behavior
    Skeleton // Use Skeleton for loading/missing images
} from "@mui/material"
import OpenInNewIcon from '@mui/icons-material/OpenInNew'; // Icon for external link

// Interface matching the structure in page.tsx
interface SimilarArticleDetail {
    image_url: string | null
    score: number // Score not used in rendering currently, but available
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
        return null; // Don't render anything if no similar articles
    }

    return (
        <Box sx={{ mt: 4 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
                Similar Articles
            </Typography>
            <Grid container spacing={2}>
                {articleEntries.map(([url, details]) => (
                    <Grid item xs={12} sm={6} md={4} key={url}>
                        <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                            {/* Make the whole card clickable */}
                            <CardActionArea
                                component={Link} // Use Link component
                                href={url}
                                target="_blank" // Open in new tab
                                rel="noopener noreferrer" // Security best practice
                                sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}
                            >
                                {details.image_url ? (
                                    <CardMedia
                                        component="img"
                                        height="140"
                                        image={details.image_url}
                                        alt={details.title || 'Article image'}
                                        sx={{ objectFit: 'cover' }} // Cover ensures image fills space nicely
                                        onError={(e: any) => { e.target.style.display = 'none'; /* Hide if image fails */ }}
                                    />
                                ) : (
                                    // Placeholder if no image
                                    <Box sx={{ height: 140, display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: 'grey.200' }}>
                                        <Typography variant="caption" color="text.secondary">No Image</Typography>
                                    </Box>
                                )}
                                <CardContent sx={{ flexGrow: 1 }}>
                                    <Typography gutterBottom variant="body1" component="div" sx={{ fontWeight: 500 }}>
                                        {details.title || 'Article'}
                                    </Typography>
                                    {/* Optionally display text preview */}
                                    {/*
                                    <Typography variant="body2" color="text.secondary">
                                        {details.text_preview}
                                    </Typography>
                                     */}
                                </CardContent>
                            </CardActionArea>
                             {/* Optional: Add an explicit link icon/button if needed */}
                             {/*
                             <Box sx={{ p: 1, display: 'flex', justifyContent: 'flex-end' }}>
                                <Link href={url} target="_blank" rel="noopener noreferrer">
                                    <OpenInNewIcon fontSize="small" />
                                </Link>
                             </Box>
                             */}
                        </Card>
                    </Grid>
                ))}
            </Grid>
        </Box>
    );
} 