"""
Content Extraction Tools
Tools for extracting content from various sources with Opik tracing
"""

from src.tools.base_tool import TracedTool, ToolArguments
from pydantic import Field, BaseModel
from typing import Type, List, Optional
import re
import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


# ===========================
# Text Extractor Tool
# ===========================

class TextExtractorArgs(ToolArguments):
    """Arguments for text extraction"""
    text: str = Field(..., description="Raw text to extract and clean")


class TextExtractorTool(TracedTool):
    """
    Extracts and cleans plain text
    
    Simple preprocessing:
    - Remove extra whitespace
    - Normalize line breaks
    - Clean special characters
    """
    
    name: str = "text_extractor"
    description: str = "Extracts and cleans plain text content"
    args_schema: Type[BaseModel] = TextExtractorArgs
    
    def _execute(self, text: str) -> dict:
        """
        Clean and normalize text
        
        Args:
            text: Raw text input
        
        Returns:
            {"content": cleaned_text, "word_count": int}
        """
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', text)
        
        # Normalize line breaks
        cleaned = re.sub(r'\n+', '\n', cleaned)
        
        # Strip leading/trailing whitespace
        cleaned = cleaned.strip()
        
        # Count words
        word_count = len(cleaned.split())
        
        logger.info(f"Text extracted: {word_count} words")
        
        return {
            "content": cleaned,
            "word_count": word_count,
            "success": True
        }


# ===========================
# YouTube Extractor Tool
# ===========================

class YouTubeExtractorArgs(ToolArguments):
    """Arguments for YouTube extraction"""
    url: str = Field(..., description="YouTube video URL")


class YouTubeExtractorTool(TracedTool):
    """
    Extracts transcript from YouTube videos
    
    Uses youtube-transcript-api to fetch transcripts
    """
    
    name: str = "youtube_extractor"
    description: str = "Extracts transcripts from YouTube videos"
    args_schema: Type[BaseModel] = YouTubeExtractorArgs
    
    def _execute(self, url: str) -> dict:
        """
        Extract YouTube transcript
        
        Args:
            url: YouTube video URL
        
        Returns:
            {"content": transcript_text, "video_id": str, "success": bool}
        """
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            
            # Extract video ID from URL
            video_id = self._extract_video_id(url)
            
            if not video_id:
                return {
                    "content": "",
                    "success": False,
                    "error": "Could not extract video ID from URL"
                }
            
            # Fetch transcript using new API
            api = YouTubeTranscriptApi()
            result = api.fetch(video_id)
            
            # Extract text from FetchedTranscript object
            # The result has a .snippets attribute containing FetchedTranscriptSnippet objects
            if hasattr(result, 'snippets'):
                # Each snippet has .text, .start, .duration attributes
                full_transcript = " ".join([snippet.text for snippet in result.snippets])
            elif isinstance(result, dict) and 'snippets' in result:
                # Fallback for dict format
                snippets = result['snippets']
                full_transcript = " ".join([snippet.text for snippet in snippets])
            else:
                # Last resort fallback
                full_transcript = str(result)
            
            word_count = len(full_transcript.split())
            
            logger.info(f"YouTube transcript extracted: {word_count} words from video {video_id}")
            
            return {
                "content": full_transcript,
                "video_id": video_id,
                "word_count": word_count,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"YouTube extraction failed: {e}")
            return {
                "content": "",
                "success": False,
                "error": str(e)
            }
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from various YouTube URL formats"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
            r'youtube\.com\/embed\/([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None


# ===========================
# PDF Extractor Tool
# ===========================

class PDFExtractorArgs(ToolArguments):
    """Arguments for PDF extraction"""
    file_path: str = Field(..., description="Path to PDF file")


class PDFExtractorTool(TracedTool):
    """
    Extracts text from PDF files
    
    Uses pypdf for PDF parsing
    """
    
    name: str = "pdf_extractor"
    description: str = "Extracts text content from PDF files"
    args_schema: Type[BaseModel] = PDFExtractorArgs
    
    def _execute(self, file_path: str) -> dict:
        """
        Extract text from PDF
        
        Args:
            file_path: Path to PDF file
        
        Returns:
            {"content": extracted_text, "page_count": int, "success": bool}
        """
        try:
            from pypdf import PdfReader
            
            # Open PDF
            reader = PdfReader(file_path)
            page_count = len(reader.pages)
            
            # Extract text from all pages
            text_parts = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            
            # Combine pages
            full_text = "\n\n".join(text_parts)
            
            # Clean up
            full_text = re.sub(r'\s+', ' ', full_text)
            word_count = len(full_text.split())
            
            logger.info(f"PDF extracted: {page_count} pages, {word_count} words")
            
            return {
                "content": full_text,
                "page_count": page_count,
                "word_count": word_count,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            return {
                "content": "",
                "success": False,
                "error": str(e)
            }


# ===========================
# Web Scraper Tool
# ===========================

class WebScraperArgs(ToolArguments):
    """Arguments for web scraping"""
    url: str = Field(..., description="Website URL to scrape")


class WebScraperTool(TracedTool):
    """
    Scrapes main content from web pages
    
    Uses BeautifulSoup to extract main text content
    """
    
    name: str = "web_scraper"
    description: str = "Scrapes main content from web pages"
    args_schema: Type[BaseModel] = WebScraperArgs
    
    def _execute(self, url: str) -> dict:
        """
        Scrape web page content
        
        Args:
            url: Website URL
        
        Returns:
            {"content": main_content, "title": str, "success": bool}
        """
        try:
            # Fetch page
            headers = {
                'User-Agent': 'Mozilla/5.0 (SONA AI Bot) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get title
            title = soup.title.string if soup.title else "Untitled"
            
            # Remove script, style, nav, footer, header
            for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                tag.decompose()
            
            # Try to find main content
            main_content = None
            
            # Common main content selectors
            for selector in ['article', 'main', '[role="main"]', '.main-content', '#content']:
                main_content = soup.select_one(selector)
                if main_content:
                    break
            
            # Fallback to body
            if not main_content:
                main_content = soup.body
            
            # Extract text
            if main_content:
                text = main_content.get_text(separator='\n', strip=True)
            else:
                text = soup.get_text(separator='\n', strip=True)
            
            # Clean up
            text = re.sub(r'\n+', '\n', text)
            text = re.sub(r'\s+', ' ', text)
            word_count = len(text.split())
            
            logger.info(f"Web content scraped: {word_count} words from {url}")
            
            return {
                "content": text,
                "title": title,
                "url": url,
                "word_count": word_count,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Web scraping failed: {e}")
            return {
                "content": "",
                "success": False,
                "error": str(e)
            }


# ===========================
# Chunker Tool
# ===========================

class ChunkerArgs(ToolArguments):
    """Arguments for text chunking"""
    text: str = Field(..., description="Text to chunk")
    chunk_size: int = Field(default=500, description="Target words per chunk")
    overlap: int = Field(default=50, description="Word overlap between chunks")


class ChunkerTool(TracedTool):
    """
    Semantic text chunking with overlap
    
    Breaks text into manageable chunks while preserving context
    """
    
    name: str = "chunker"
    description: str = "Semantically chunks text with overlap for context preservation"
    args_schema: Type[BaseModel] = ChunkerArgs
    
    def _execute(self, text: str, chunk_size: int = 500, overlap: int = 50) -> dict:
        """
        Chunk text semantically
        
        Args:
            text: Full text to chunk
            chunk_size: Target words per chunk
            overlap: Words to overlap between chunks
        
        Returns:
            {"chunks": List[str], "chunk_count": int}
        """
        # Split by paragraphs first (better semantic boundaries)
        paragraphs = text.split('\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        chunks = []
        current_chunk = []
        current_word_count = 0
        
        for paragraph in paragraphs:
            words = paragraph.split()
            para_word_count = len(words)
            
            # If adding this paragraph would exceed chunk_size, start new chunk
            if current_word_count + para_word_count > chunk_size and current_chunk:
                # Save current chunk
                chunk_text = ' '.join(current_chunk)
                chunks.append(chunk_text)
                
                # Start new chunk with overlap
                if overlap > 0 and current_word_count > overlap:
                    # Take last 'overlap' words from current chunk
                    overlap_words = ' '.join(current_chunk).split()[-overlap:]
                    current_chunk = overlap_words
                    current_word_count = len(overlap_words)
                else:
                    current_chunk = []
                    current_word_count = 0
            
            # Add paragraph to current chunk
            current_chunk.extend(words)
            current_word_count += para_word_count
        
        # Don't forget the last chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append(chunk_text)
        
        logger.info(f"Text chunked into {len(chunks)} chunks (target: {chunk_size} words/chunk)")
        
        return {
            "chunks": chunks,
            "chunk_count": len(chunks),
            "success": True
        }


# Tool instances
text_extractor = TextExtractorTool()
youtube_extractor = YouTubeExtractorTool()
pdf_extractor = PDFExtractorTool()
web_scraper = WebScraperTool()
chunker = ChunkerTool()
