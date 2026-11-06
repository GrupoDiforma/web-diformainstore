// Function to sanitize captions and prevent XSS
function sanitizeElptCaption(caption) {
    if (typeof caption !== 'string') return caption;
    
    // Remove any HTML to prevent XSS
    var tempDiv = jQuery('<div>');
    tempDiv.text(caption);
    return tempDiv.html(); // Returns escaped text
}

// Safe function to decode HTML entities without executing JavaScript
function safeDecodeHtml(str) {
    if (typeof str !== 'string') return str;
    
    // Check if it contains dangerous patterns before decoding
    var dangerousPatterns = [
        /&lt;script/i,
        /&lt;img[^&]*onerror/i,
        /&lt;[^&]*on\w+=/i,
        /javascript:/i,
        /&lt;iframe/i,
        /&lt;object/i,
        /&lt;embed/i
    ];
    
    for (var i = 0; i < dangerousPatterns.length; i++) {
        if (dangerousPatterns[i].test(str)) {
            // If it contains dangerous patterns, return only text without decoding
            return str.replace(/&[#\w]+;/g, '').replace(/[<>]/g, '');
        }
    }
    
    // If it doesn't contain dangerous patterns, decode safely
    var txt = document.createElement('textarea');
    txt.innerHTML = str;
    var decoded = txt.value;
    
    // Remove any remaining HTML tags as an extra security measure
    decoded = decoded.replace(/<[^>]*>/g, '');
    
    return decoded;
}

// Function to sanitize all images in the DOM
function sanitizeAllImages() {
    jQuery('.elpt-portfolio img[title], a.elpt-portfolio-lightbox img[title]').each(function() {
        var $img = jQuery(this);
        var originalTitle = $img.attr('title');
        if (originalTitle) {
            // Decode HTML entities safely, then sanitize
            var decodedTitle = safeDecodeHtml(originalTitle);
            var sanitizedTitle = sanitizeElptCaption(decodedTitle);
            $img.attr('title', sanitizedTitle);
        }
    });
}

// Execute sanitization immediately
jQuery(document).ready(function() {
    sanitizeAllImages();
});

jQuery(window).on('load', function () {
    // Sanitize again on load
    sanitizeAllImages();
    
    if (jQuery(".elpt-portfolio-content").length) {
        
        // Process video links with data attributes
        jQuery('a.elpt-portfolio-video-lightbox').each(function() {
            var videoUrl = jQuery(this).attr('data-video');
            if (videoUrl) {
                // Modify link behavior to open video in lightbox
                jQuery(this).on('click', function(e) {
                    e.preventDefault();
                    
                    // Open lightbox with video
                    if (videoUrl.indexOf('youtube.com') > -1 || videoUrl.indexOf('youtu.be') > -1) {
                        // Youtube video
                        var videoId = getYoutubeId(videoUrl);
                        if (videoId) {
                            // Usar o lightbox do SimpleLightbox
                            var embedUrl = 'https://www.youtube.com/embed/' + videoId + '?autoplay=1&rel=0';
                            openVideoLightbox(embedUrl);
                        }
                    } else if (videoUrl.indexOf('vimeo.com') > -1) {
                        // Vimeo video
                        var videoId = getVimeoId(videoUrl);
                        if (videoId) {
                            // Usar o lightbox do SimpleLightbox
                            var embedUrl = 'https://player.vimeo.com/video/' + videoId + '?autoplay=1&title=0&byline=0&portrait=0';
                            openVideoLightbox(embedUrl);
                        }
                    }
                    
                    return false;
                });
            }
        });
        
        // Prevent Elementor Lightbox from being triggered for our items
        jQuery('a.elpt-portfolio-lightbox, a.elpt-portfolio-video-lightbox').each(function() {
            // Remove any class that might trigger Elementor's lightbox
            jQuery(this).removeClass('elementor-clickable');
            // Add attribute that prevents Elementor from opening its lightbox
            jQuery(this).attr('data-elementor-open-lightbox', 'no');
            
            // Prevent event propagation to avoid Elementor capturing it (except for videos that already have handlers)
            if (!jQuery(this).hasClass('elpt-portfolio-video-lightbox') || !jQuery(this).attr('data-video')) {
                jQuery(this).on('click', function(e) {
                    e.stopPropagation();
                });
            }
        });
        
        // Sanitize again before initializing lightbox
        sanitizeAllImages();
        
        // Initialize lightbox for images with safe configuration
        var lightboxInstance = jQuery('a.elpt-portfolio-lightbox').simpleLightbox({
            captions: true,
            disableScroll: false,
            rel: true,
            // Hook to sanitize captions in real time
            additionalHtml: false
        });
        
                // Override SimpleLightbox library to use text instead of HTML
        // Intercepts when captions are added
        var originalAppendTo = jQuery.fn.appendTo;
        jQuery.fn.appendTo = function(selector) {
            var result = originalAppendTo.apply(this, arguments);
            
            // If it's a caption being added
            if (this.hasClass && this.hasClass('sl-caption')) {
                var captionContent = this.html();
                if (captionContent) {
                    var decodedContent = safeDecodeHtml(captionContent);
                    var sanitizedContent = sanitizeElptCaption(decodedContent);
                    this.text(sanitizedContent); // Use text() instead of html()
                }
            }
            
            return result;
        };
        
                // Intercept and sanitize captions dynamically
        // Observe DOM changes to sanitize new captions
        var observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.addedNodes) {
                    mutation.addedNodes.forEach(function(node) {
                        if (node.nodeType === 1) { // Element node
                            var $node = jQuery(node);
                            if ($node.hasClass('sl-caption') || $node.find('.sl-caption').length > 0) {
                                var $caption = $node.hasClass('sl-caption') ? $node : $node.find('.sl-caption');
                                var captionHtml = $caption.html();
                                if (captionHtml) {
                                    var decodedCaption = safeDecodeHtml(captionHtml);
                                    var sanitizedCaption = sanitizeElptCaption(decodedCaption);
                                    $caption.text(sanitizedCaption); // Use .text() instead of .html()
                                }
                            }
                        }
                    });
                }
            });
        });
        
        // Observe changes in the body
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    // Function to get YouTube video ID from URL
    function getYoutubeId(url) {
        var regExp = /^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#&?]*).*/;
        var match = url.match(regExp);
        return (match && match[7].length == 11) ? match[7] : false;
    }
    
    // Function to get Vimeo video ID from URL
    function getVimeoId(url) {
        var regExp = /^.*(vimeo\.com\/)((channels\/[A-z]+\/)|(groups\/[A-z]+\/videos\/))?([0-9]+)/;
        var match = url.match(regExp);
        return match ? match[5] : false;
    }
    
    // Function to open lightbox with embedded video
    function openVideoLightbox(embedUrl) {
        // Create a dark overlay
        var overlay = jQuery('<div id="elpt-video-overlay"></div>')
            .css({
                'position': 'fixed',
                'top': 0,
                'left': 0,
                'width': '100%',
                'height': '100%',
                'background-color': 'rgba(0,0,0,0.9)',
                'z-index': 9999,
                'display': 'flex',
                'justify-content': 'center',
                'align-items': 'center'
            })
            .appendTo('body');
            
        // Create video container (responsive size computed in sizeVideoContainer)
        var videoContainer = jQuery('<div id="elpt-video-container"></div>')
            .css({
                'position': 'relative',
                'box-sizing': 'border-box'
            })
            .appendTo(overlay);

        // Create video iframe
        var iframe = jQuery('<iframe></iframe>')
            .attr({
                'src': embedUrl,
                'frameborder': '0',
                'allowfullscreen': 'true',
                'allow': 'autoplay; fullscreen'
            })
            .css({
                'position': 'absolute',
                'top': 0,
                'left': 0,
                'width': '100%',
                'height': '100%'
            })
            .appendTo(videoContainer);

        // Size the container to fit the viewport while keeping a 16:9 ratio.
        // Constrained by both width (90vw, max 900px) and height (90vh) so it
        // never overflows on mobile or with vertical videos. Recomputed on resize.
        function sizeVideoContainer() {
            var maxWidth = Math.min(window.innerWidth * 0.9, 900);
            var maxHeight = window.innerHeight * 0.9;
            var width = maxWidth;
            var height = width * 9 / 16;
            if (height > maxHeight) {
                height = maxHeight;
                width = height * 16 / 9;
            }
            videoContainer.css({
                'width': Math.round(width) + 'px',
                'height': Math.round(height) + 'px'
            });
        }
        sizeVideoContainer();

        // Create close button, fixed to the viewport so it is always visible/tappable
        var closeButton = jQuery('<div id="elpt-video-close">×</div>')
            .css({
                'position': 'fixed',
                'top': '12px',
                'right': '16px',
                'width': '44px',
                'height': '44px',
                'line-height': '44px',
                'text-align': 'center',
                'color': 'white',
                'font-size': '34px',
                'cursor': 'pointer',
                'z-index': 10000
            })
            .appendTo(overlay);

        function closeVideoLightbox() {
            overlay.remove();
            jQuery(window).off('resize.elptVideo orientationchange.elptVideo');
            jQuery(document).off('keydown.elptVideo');
        }

        // Add click event to close lightbox
        closeButton.on('click', closeVideoLightbox);

        // Close lightbox when clicking outside video
        overlay.on('click', function(e) {
            if (e.target === this) {
                closeVideoLightbox();
            }
        });

        // Close lightbox when pressing ESC
        jQuery(document).on('keydown.elptVideo', function(e) {
            if (e.keyCode === 27) { // ESC key
                closeVideoLightbox();
            }
        });

        // Recompute size on viewport changes (resize / device rotation)
        jQuery(window).on('resize.elptVideo orientationchange.elptVideo', sizeVideoContainer);
    }
});