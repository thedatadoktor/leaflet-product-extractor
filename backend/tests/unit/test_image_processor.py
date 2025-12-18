"""
Unit tests for ImageProcessor
"""
import pytest
import numpy as np
from app.utils.image_processor import ImageProcessor


class TestImageProcessor:
    """Test ImageProcessor functionality"""
    
    @pytest.fixture
    def processor(self):
        """Create ImageProcessor instance"""
        return ImageProcessor(max_width=800, max_height=800)
    
    @pytest.fixture
    def sample_image(self):
        """Create sample test image"""
        return np.random.randint(0, 255, (1000, 1000, 3), dtype=np.uint8)
    
    @pytest.fixture
    def sample_gray_image(self):
        """Create sample grayscale image"""
        return np.random.randint(0, 255, (1000, 1000), dtype=np.uint8)
    
    def test_to_grayscale(self, processor, sample_image):
        """Test grayscale conversion"""
        gray = processor.to_grayscale(sample_image)
        assert len(gray.shape) == 2
        assert gray.dtype == np.uint8
    
    def test_to_grayscale_already_gray(self, processor, sample_gray_image):
        """Test grayscale conversion on already gray image"""
        result = processor.to_grayscale(sample_gray_image)
        assert np.array_equal(result, sample_gray_image)
    
    def test_resize_if_needed_large_image(self, processor, sample_image):
        """Test resize on image exceeding limits"""
        resized = processor.resize_if_needed(sample_image)
        h, w = resized.shape[:2]
        assert w <= processor.max_width
        assert h <= processor.max_height
    
    def test_resize_if_needed_small_image(self, processor):
        """Test resize on image within limits"""
        small_image = np.random.randint(0, 255, (500, 500, 3), dtype=np.uint8)
        result = processor.resize_if_needed(small_image)
        assert result.shape == small_image.shape
    
    def test_denoise(self, processor, sample_gray_image):
        """Test denoising"""
        denoised = processor.denoise(sample_gray_image)
        assert denoised.shape == sample_gray_image.shape
        assert denoised.dtype == np.uint8
    
    def test_enhance_contrast(self, processor, sample_gray_image):
        """Test contrast enhancement"""
        enhanced = processor.enhance_contrast(sample_gray_image)
        assert enhanced.shape == sample_gray_image.shape
        assert enhanced.dtype == np.uint8
    
    def test_adaptive_threshold(self, processor, sample_gray_image):
        """Test adaptive thresholding"""
        thresh = processor.adaptive_threshold(sample_gray_image)
        assert thresh.shape == sample_gray_image.shape
        # Binary image should only have 0 and 255
        assert set(np.unique(thresh)).issubset({0, 255})
