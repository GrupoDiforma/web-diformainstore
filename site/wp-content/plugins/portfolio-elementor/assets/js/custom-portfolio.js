jQuery(window).on('load', function () {


    // Aqui eu consigo alternar entre a versao paginada ou normal, apenas pela classe
    // vamos deixar tudo no mesmo arquivo, e mudar a classe atraves do elementor.
    // vamos precisar passar algumas informacoes para o JS (numero de paginas, etc)

    // Talvez de para deixar o packery etc tudo na mesma variavel, porque o packery tambem pode ser paginado

    if ( jQuery( ".elpt-portfolio-content" ).length ) {
        // IMPORTANT: Use :not(.elpt-portfolio-content-isotope-pro) to prevent double Isotope
        // initialization. Elements with -pro class are handled by $container for pagination.

        //Isotope Layout (masonry without pagination)
        var $grid = jQuery('.elpt-portfolio-content-isotope:not(.elpt-portfolio-content-isotope-pro)').isotope({
            //layoutMode: 'packery',
            layoutMode: 'masonry',
            itemSelector: '.portfolio-item-wrapper'
        });

        $grid.imagesLoaded().progress( function() {
            $grid.isotope('layout');
        });

        //Packery Layout (without pagination)
        var $packery = jQuery('.elpt-portfolio-content-packery:not(.elpt-portfolio-content-isotope-pro)').isotope({
            layoutMode: 'packery',
            itemSelector: '.portfolio-item-wrapper'
        });

        $packery.imagesLoaded().progress( function() {
            $packery.isotope('layout');
        });

        //fitRows Layout (for Special Grid 7 and similar, without pagination)
        var $fitrows = jQuery('.elpt-portfolio-content-fitrows:not(.elpt-portfolio-content-isotope-pro)').isotope({
            layoutMode: 'fitRows',
            itemSelector: '.portfolio-item-wrapper'
        });

        $fitrows.imagesLoaded().progress( function() {
            $fitrows.isotope('layout');
        });

        /*
        * Paginated Isotope
        */
        //https://codepen.io/TimRizzo/details/ervrRq
        //https://codepen.io/Igorxp5/pen/ojJLQE

        var itemSelector = ".portfolio-item-wrapper";

        // Support masonry, packery, and fitRows pagination
        var $container = jQuery('.elpt-portfolio-content-isotope-pro').isotope({
            layoutMode: 'masonry',
            itemSelector: itemSelector
        });

        // Check layout mode based on additional classes
        if ($container.hasClass('elpt-portfolio-content-fitrows')) {
            // Special Grid 7 - Alternate Rows 1
            $container.isotope('option', { layoutMode: 'fitRows' });
        } else if ($container.hasClass('elpt-portfolio-content-packery')) {
            // Grid Builder
            $container.isotope('option', { layoutMode: 'packery' });
        }

        $container.imagesLoaded().progress( function() {
            $container.isotope('layout');
        });

        // Pagination Variables
        var itemsPerPageDefault = 10; // Default value

        // Prefer the per-container data attribute (works in shortcode + Elementor
        // contexts and per container). Fall back to the legacy gridSettings global.
        var containerPerPage = parseInt($container.attr('data-items-per-page'), 10);
        if (!isNaN(containerPerPage) && containerPerPage > 0) {
            itemsPerPageDefault = containerPerPage;
        } else if (typeof gridSettings !== 'undefined' && gridSettings.itemsPerPageDefault !== undefined) {
            itemsPerPageDefault = gridSettings.itemsPerPageDefault;
        }

        var itemsPerPage = defineItemsPerPage();
        var currentNumberPages = 1;
        var currentPage = 1;
        var currentFilter = '*';
        var filterAtribute = 'data-filter';
        var pageAtribute = 'data-page';
        var pagerClass = 'isotope-pager';

        // ===========================================
        // Fixed Layout Mode: Race Condition Prevention
        // ===========================================
        // These variables prevent race conditions when users click rapidly on
        // pagination or filters. Only affects Fixed Layout Mode (Grid Builder).
        //
        // KEY CONCEPT: Each filter/pagination click should be treated as a fresh start.
        // We cache the original DOM order and sizes, then restore from cache on each operation.
        var fixedLayoutEventId = 0;           // Invalidates outdated event handlers
        var fixedLayoutOriginalOrder = [];    // Cache of items in original DOM order
        var fixedLayoutInitialized = false;   // Whether cache has been built
        var fixedLayoutCompletedEventId = 0;  // Tracks which eventId has completed (prevents infinite loop)

        // Debug logging for Fixed Layout Mode (disabled in production)
        var FIXED_LAYOUT_DEBUG = false;
        function fixedLayoutLog(message, data) {
            if (FIXED_LAYOUT_DEBUG) {
                if (data !== undefined) {
                    console.log('[FixedLayout]', message, data);
                } else {
                    console.log('[FixedLayout]', message);
                }
            }
        }

        /**
         * Initialize Fixed Layout cache - stores original DOM order of all items.
         * This should be called once on page load for Fixed Layout grids.
         */
        function initFixedLayoutCache($containerElement) {
            if (fixedLayoutInitialized) {
                return;
            }

            var $allItems = $containerElement.children('.portfolio-item-wrapper');
            fixedLayoutOriginalOrder = [];

            $allItems.each(function(index) {
                fixedLayoutOriginalOrder.push({
                    element: this,
                    originalIndex: index
                });
            });

            fixedLayoutInitialized = true;
            fixedLayoutLog('Cache initialized with ' + fixedLayoutOriginalOrder.length + ' items');
        }

        /**
         * Reset all position classes to original state based on cached order.
         * This ensures each operation starts from a clean, consistent state.
         */
        function resetFixedLayoutPositions($containerElement) {
            var $allItems = $containerElement.children('.portfolio-item-wrapper');

            // Remove ALL position classes from ALL items
            $allItems.removeClass(function(index, className) {
                return (className.match(/\belpt-grid-pos-\d+\b/g) || []).join(' ');
            });

            fixedLayoutLog('All position classes removed');
        }

        /**
         * Scroll to the top of the grid container INSTANTLY (no animation).
         * This must happen BEFORE any layout processing so user sees the grid top first.
         * Only applies to Fixed Layout Mode (Grid Builder).
         *
         * Addons can modify the scroll target via 'powerfolio:scroll_target' filter.
         *
         * @param {jQuery} $containerElement - The grid container element
         */
        function scrollToGridTop($containerElement) {
            if (!$containerElement || $containerElement.length === 0) {
                return;
            }

            var gridTop = $containerElement.offset().top;
            var margin = 100; // pixels above the grid to account for headers/nav
            var targetScroll = Math.max(0, gridTop - margin);
            var currentScroll = jQuery(window).scrollTop();

            // Allow addons to modify scroll target (e.g., scroll to page top instead of grid top)
            var scrollData = {
                target: targetScroll,
                gridTop: gridTop,
                margin: margin,
                container: $containerElement
            };
            jQuery(document).trigger('powerfolio:scroll_target', [scrollData]);
            targetScroll = scrollData.target;

            // Only scroll if user is below the target (don't scroll up if already above)
            if (currentScroll > targetScroll) {
                // INSTANT scroll - no animation, must complete before layout processing
                window.scrollTo(0, targetScroll);

                fixedLayoutLog('Scrolled to: ' + targetScroll + 'px');
            }
        }

        // Resize handler with debounce
        // Fixed Layout Mode requires special handling to maintain positions
        var resizeTimeout;
        jQuery(window).resize(function(){
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(function() {
                // Check if Fixed Layout Mode is enabled (only for Grid Builder)
                var $gridBuilder = jQuery('.elpt-portfolio-content-packery.elpt-portfolio-grid-builder');
                var isFixedLayout = $gridBuilder.length > 0 && $gridBuilder.hasClass('elpt-fixed-layout-mode');

                if ($container.length > 0) {
                    // Has pagination: maintain current page and filter
                    if (isFixedLayout) {
                        fixedLayoutLog('Resize detected - triggering fresh layout');
                        // For Fixed Layout, just trigger goToPage which will handle everything
                    }
                    goToPage(currentPage);
                } else {
                    // No pagination: just refresh layout
                    if (isFixedLayout) {
                        // Fixed Layout without pagination: re-apply positions
                        applyFixedLayoutPositionsFromIsotope($packery);
                        $packery.isotope('layout');
                    } else {
                        // Normal grids: just trigger layout refresh
                        $grid.isotope('layout');
                        $packery.isotope('layout');
                        $fitrows.isotope('layout');
                    }
                }
            }, 150); // 150ms debounce
        });



        // update items based on current filters
        function changeFilter(selector) {
            $container.isotope({ filter: selector }
        ); }


        function getFilterSelector() {
            var selector = itemSelector;
            if (currentFilter != '*') {
              selector += currentFilter;
            }
            return selector;
        }

        function goToPage(n) {
            // Check if Fixed Layout Mode is enabled (only for Grid Builder)
            var $gridBuilder = jQuery('.elpt-portfolio-content-packery.elpt-portfolio-grid-builder');
            var isFixedLayout = $gridBuilder.length > 0 && $gridBuilder.hasClass('elpt-fixed-layout-mode');

            currentPage = n;

            var selector = getFilterSelector();
            selector += '[' + pageAtribute + '="' + currentPage + '"]';

            if (isFixedLayout) {
                // FIXED LAYOUT MODE - Fresh Start Approach
                // ========================================
                // Each call to goToPage CANCELS any previous operation and starts fresh.
                // No queuing, no waiting - just invalidate old handlers and restart.
                //
                // Strategy:
                // 1. Increment eventId to invalidate ALL previous handlers
                // 2. Initialize cache if needed (first run only)
                // 3. Reset all position classes to clean state
                // 4. Apply position classes for visible items (DOM order)
                // 5. Apply Isotope filter and layout
                // 6. On arrangeComplete, correct positions based on visual order
                // 7. Final layout pass (deferred with setTimeout to break recursion)

                // Step 1: Invalidate ALL previous operations
                fixedLayoutEventId++;
                var currentEventId = fixedLayoutEventId;

                fixedLayoutLog('goToPage(' + n + ') START - eventId: ' + currentEventId + ' (previous operations cancelled)');

                // Step 2: Initialize cache on first run
                initFixedLayoutCache($container);

                // Step 3: Reset ALL position classes to clean state
                resetFixedLayoutPositions($container);

                // Step 4: Apply position classes for items matching selector (DOM order)
                applyFixedLayoutPositionsForCurrentFilter($container, selector);

                // Step 5: Apply Isotope filter
                changeFilter(selector);

                // Step 6: Force layout - Isotope will calculate positions
                $container.isotope('layout');

                fixedLayoutLog('goToPage(' + n + ') - layout triggered, eventId: ' + currentEventId);

                // Step 7: After Isotope arranges, correct positions and do final layout
                $container.isotope('once', 'arrangeComplete', function() {
                    // CRITICAL: Ignore if this event is outdated (user clicked something else)
                    if (currentEventId !== fixedLayoutEventId) {
                        fixedLayoutLog('arrangeComplete SKIPPED - outdated eventId: ' + currentEventId + ', current: ' + fixedLayoutEventId);
                        return;
                    }

                    // Prevent infinite loop: if this eventId already completed its final pass, ignore
                    // This happens when layout() triggers another arrangeComplete
                    if (currentEventId <= fixedLayoutCompletedEventId) {
                        fixedLayoutLog('arrangeComplete SKIPPED - eventId ' + currentEventId + ' already completed');
                        return;
                    }

                    fixedLayoutLog('goToPage(' + n + ') arrangeComplete - eventId: ' + currentEventId);

                    // Correct position classes based on Isotope's visual order
                    applyFixedLayoutPositionsFromIsotope($container);

                    // Mark this event as completed BEFORE the final layout
                    // This prevents the arrangeComplete triggered by layout() from running again
                    fixedLayoutCompletedEventId = currentEventId;

                    // Final layout pass - deferred to break synchronous chain
                    setTimeout(function() {
                        // Check again - user might have clicked during the timeout
                        if (currentEventId !== fixedLayoutEventId) {
                            fixedLayoutLog('setTimeout SKIPPED - outdated eventId: ' + currentEventId);
                            return;
                        }

                        fixedLayoutLog('goToPage(' + n + ') FINAL layout - eventId: ' + currentEventId);
                        $container.isotope('layout');

                        fixedLayoutLog('goToPage(' + n + ') COMPLETE - eventId: ' + currentEventId);

                        // Trigger event for addons (e.g., parallax effects)
                        jQuery(document).trigger('powerfolio:layout_complete', [$container, currentPage, currentFilter]);
                    }, 0);
                });
            } else {
                // Normal mode: just apply filter (unchanged behavior)
                changeFilter(selector);

                // Trigger event for addons after layout settles
                setTimeout(function() {
                    jQuery(document).trigger('powerfolio:layout_complete', [$container, currentPage, currentFilter]);
                }, 100);
            }
        }

        /**
         * Fixed Layout Mode: Apply position classes based on current filter selector
         * This applies classes BEFORE Isotope calculates positions, using DOM order.
         * Used to ensure items have correct sizes during initial layout calculation.
         */
        function applyFixedLayoutPositionsForCurrentFilter($containerElement, filterSelector) {
            var $allItems = $containerElement.children('.portfolio-item-wrapper');

            // Remove all position classes from all items
            $allItems.removeClass(function(index, className) {
                return (className.match(/\belpt-grid-pos-\d+\b/g) || []).join(' ');
            });

            // Get items matching the filter selector
            var $matchingItems = $allItems.filter(filterSelector);

            // Apply position classes in DOM order
            $matchingItems.each(function(index) {
                jQuery(this).addClass('elpt-grid-pos-' + (index + 1));
            });
        }

        function defineItemsPerPage() {
            var pages = itemsPerPageDefault;

            return pages;
        }

        function setPagination() {

            var SettingsPagesOnItems = function(){

                var item = 1;
                var page = 1;
                var selector = getFilterSelector();

                $container.children(selector).each(function(){
                    if( item > itemsPerPage ) {
                        page++;
                        item = 1;
                    }
                    jQuery(this).attr(pageAtribute, page);
                    item++;
                });

                currentNumberPages = page;

            }();

            var CreatePagers = function() {

                var $isotopePager = ( jQuery('.'+pagerClass).length == 0 ) ? jQuery('<div class="'+pagerClass+'"></div>') : jQuery('.'+pagerClass);

                $isotopePager.html('');

                for( var i = 0; i < currentNumberPages; i++ ) {
                    var $pager = jQuery('<a href="javascript:void(0);" class="pager" '+pageAtribute+'="'+(i+1)+'"></a>');
                        $pager.html(i+1);

                        $pager.click(function(){
                            jQuery('.isotope-pager .active').removeClass('active');
                            jQuery(this).addClass('active');
                            var page = jQuery(this).eq(0).attr(pageAtribute);

                            // Scroll to grid top BEFORE processing (Fixed Layout Mode)
                            var $gridBuilder = jQuery('.elpt-portfolio-content-packery.elpt-portfolio-grid-builder');
                            if ($gridBuilder.length > 0 && $gridBuilder.hasClass('elpt-fixed-layout-mode')) {
                                scrollToGridTop($container);
                            }

                            goToPage(page);
                        });

                    $pager.appendTo($isotopePager);
                }

                $container.after($isotopePager);

            }();

        }

        setPagination();
        goToPage(1);

        /**
         * Fixed Layout Mode: Apply position classes based on Isotope's visual order
         *
         * This function uses Isotope's internal filteredItems array to get elements
         * in their correct visual order (not DOM order). This is essential for
         * Fixed Layout Mode where CSS classes determine element sizes/positions.
         *
         * @param {jQuery} $isotopeContainer - The Isotope container element
         */
        function applyFixedLayoutPositionsFromIsotope($isotopeContainer) {
            var isotope = $isotopeContainer.data('isotope');
            if (!isotope) {
                return;
            }

            var $allItems = $isotopeContainer.children('.portfolio-item-wrapper');

            // Remove all position classes from all items
            $allItems.removeClass(function(index, className) {
                return (className.match(/\belpt-grid-pos-\d+\b/g) || []).join(' ');
            });

            // Get filtered items in Isotope's visual order
            var filteredItems = isotope.filteredItems;
            if (!filteredItems || filteredItems.length === 0) {
                return;
            }

            // Apply position classes based on visual order
            filteredItems.forEach(function(item, index) {
                jQuery(item.element).addClass('elpt-grid-pos-' + (index + 1));
            });
        }

        /**
         * Fixed Layout Mode: Apply position classes for filtered items (pre-pagination)
         *
         * This function is called BEFORE pagination is applied. It assigns position
         * classes to ALL items matching the filter, which will then be narrowed down
         * by pagination. Uses DOM order since Isotope hasn't filtered yet.
         *
         * Note: This is kept for the initial filter application. After Isotope
         * arranges items, applyFixedLayoutPositionsFromIsotope() corrects the order.
         *
         * @param {jQuery} $containerElement - The grid container element
         * @param {string} filterValue - The filter selector (e.g., '.category-1' or '*')
         */
        function applyFixedLayoutFilter($containerElement, filterValue) {
            var $allItems = $containerElement.children('.portfolio-item-wrapper');

            // Determine which items match the filter
            var $matchingItems;
            if (filterValue === '*') {
                $matchingItems = $allItems;
            } else {
                $matchingItems = $allItems.filter(filterValue);
            }

            // Remove all position classes from all items
            $allItems.removeClass(function(index, className) {
                return (className.match(/\belpt-grid-pos-\d+\b/g) || []).join(' ');
            });

            // Apply initial position classes (will be corrected after Isotope arranges)
            $matchingItems.each(function(visualIndex) {
                jQuery(this).addClass('elpt-grid-pos-' + (visualIndex + 1));
            });
        }

        // On Click Actions
        jQuery('.elpt-portfolio-filter').on('click', 'button', function () {
            jQuery('.elpt-portfolio-filter button').removeClass('item-active');
            jQuery(this).addClass('item-active');

            var filterValue = jQuery(this).attr(filterAtribute);
            var filter = filterValue;
            currentFilter = filter;

            // Check if Fixed Layout Mode is enabled (only for Grid Builder)
            var $gridBuilder = jQuery('.elpt-portfolio-content-packery.elpt-portfolio-grid-builder');
            var isFixedLayout = $gridBuilder.hasClass('elpt-fixed-layout-mode');

            if (isFixedLayout) {
                fixedLayoutLog('Filter clicked: ' + filterValue);

                // If pagination is NOT enabled, apply Isotope filter directly
                if ($container.length === 0) {
                    // No pagination: apply Isotope filter on $packery
                    // Use Fresh Start Approach - cancel previous and restart

                    fixedLayoutEventId++;
                    var currentEventId = fixedLayoutEventId;

                    fixedLayoutLog('Filter START (no pagination) - eventId: ' + currentEventId);

                    // Reset and apply position classes
                    resetFixedLayoutPositions($packery);
                    applyFixedLayoutFilter($gridBuilder, filterValue);

                    $packery.isotope({ filter: filterValue });
                    $packery.isotope('layout');

                    // After Isotope arranges, correct the position classes and do final layout
                    $packery.isotope('once', 'arrangeComplete', function() {
                        if (currentEventId !== fixedLayoutEventId) {
                            fixedLayoutLog('Filter arrangeComplete SKIPPED - outdated eventId: ' + currentEventId);
                            return;
                        }

                        // Prevent infinite loop: if this eventId already completed, ignore
                        if (currentEventId <= fixedLayoutCompletedEventId) {
                            fixedLayoutLog('Filter arrangeComplete SKIPPED - eventId ' + currentEventId + ' already completed');
                            return;
                        }

                        fixedLayoutLog('Filter arrangeComplete (no pagination) - eventId: ' + currentEventId);

                        applyFixedLayoutPositionsFromIsotope($packery);

                        // Mark as completed before final layout
                        fixedLayoutCompletedEventId = currentEventId;

                        setTimeout(function() {
                            if (currentEventId !== fixedLayoutEventId) {
                                return;
                            }

                            fixedLayoutLog('Filter FINAL layout (no pagination) - eventId: ' + currentEventId);
                            $packery.isotope('layout');

                            fixedLayoutLog('Filter COMPLETE (no pagination) - eventId: ' + currentEventId);

                            // Trigger event for addons (Fixed Layout without pagination)
                            jQuery(document).trigger('powerfolio:layout_complete', [$packery, 1, filterValue]);
                        }, 0);
                    });
                }
                // If pagination IS enabled, we'll handle it below with setPagination + goToPage
            } else {
                // Normal: Use Isotope filter (current behavior for non-Fixed Layout)
                $grid.isotope({
                    filter: filterValue
                });
                $packery.isotope({
                    filter: filterValue
                });
                $fitrows.isotope({
                    filter: filterValue
                });

                // Trigger event for addons after filter layout settles (non-paginated grids)
                if ($container.length === 0) {
                    setTimeout(function() {
                        // Pass whichever grid is active
                        var $activeGrid = $packery.length > 0 ? $packery : ($grid.length > 0 ? $grid : $fitrows);
                        jQuery(document).trigger('powerfolio:layout_complete', [$activeGrid, 1, filterValue]);
                    }, 100);
                }
            }

            // Only call pagination functions if pagination is enabled
            // ($container targets .elpt-portfolio-content-isotope-pro which only exists with pagination)
            if ($container.length > 0) {
                if (isFixedLayout) {
                    // Scroll to grid top BEFORE processing
                    scrollToGridTop($container);
                    fixedLayoutLog('Filter with pagination - calling setPagination + goToPage(1)');
                }
                setPagination();
                goToPage(1);
            }
        });

        // Trigger initialization event for addons
        // Provides references to all grid containers for addon initialization
        jQuery(document).trigger('powerfolio:grid_initialized', [{
            grid: $grid,
            packery: $packery,
            fitrows: $fitrows,
            container: $container
        }]);

    }

});
